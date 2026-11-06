"""Live scaling benchmark for your Mandelbrot program, with a window you can watch and pause.

Runs your program once per setting (feeding it the answers automatically, no plot window),
saves the time of every setting to results.txt / results.csv, and draws the results live.

  sizes      : 600x400 ... 9600x6400  (+300x200 each time)
  max steps  : 50, 100, 150, 200
  processors : 1, 2, 4, 8, 16
  repeats    : REPS runs per setting (default 3); the MEDIAN is the number to trust
  ORDER      : theoretical quickest -> longest (from a simple cost model, see estimate_seconds)

Usage:   python bench_live.py [path/to/your_program.py]
Options: REPS=1 python bench_live.py     (3x faster, rougher)
         QUICK=1 python bench_live.py    (tiny test grid, about a minute)
In the window: [Pause]/[Resume] (or press the space bar) freezes the running program completely
and does not count the paused time. [Stop] or closing the window stops safely.
Everything finished so far is saved. Run again and it carries on where it stopped.
"""
import csv, os, signal, statistics, subprocess, sys, threading, time
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.ticker import FuncFormatter, LogLocator

program = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/Desktop/mandelbrot-final.py")
reps = int(os.environ.get("REPS", "3"))
outdir = os.path.expanduser(os.environ.get("OUT", "~/Documents/Mandelbrot_Scaling_Live"))
quick = os.environ.get("QUICK") == "1"

if quick:
    sizes = [(300 * k, 200 * k) for k in (2, 3, 4)]
    steps_list, procs_list = [50, 100], [1, 2]
else:
    sizes = [(300 * k, 200 * k) for k in range(2, 33)]      # 600x400 ... 9600x6400
    steps_list, procs_list = [50, 100, 150, 200], [1, 2, 4, 8, 16]

YMAX, YMIN, XMAX, XMIN = 1, -1, 0.5, -2                      # whole Mandelbrot set
COLOUR_CHOICE = 1                                            # magma

def estimate_seconds(w, h, steps, procs):
    """Rough 'theory': time = start-up + (pixels x average iterations x cost per iteration) / processors.
    ~25% of the pixels are inside the set and always cost all `steps`; the rest escape early (~10 steps)."""
    avg_iterations = 0.25 * steps + 10
    work = w * h * avg_iterations * 60e-9          # ~60 ns per iteration in plain Python (your Mac, 1 core)
    startup = 1.0 + 0.08 * procs                   # starting Python + the helpers
    return startup + work / procs

# ---------- the plan, quickest first ----------
plan = [(w, h, s, p) for (w, h) in sizes for s in steps_list for p in procs_list]
plan.sort(key=lambda t: estimate_seconds(*t))

if not os.path.isfile(program):
    sys.exit(f"Can't find {program} - pass its path as an argument")
os.makedirs(outdir, exist_ok=True)
txt_path, csv_path = os.path.join(outdir, "results.txt"), os.path.join(outdir, "results.csv")
HEADER = ["width", "height", "steps", "processors", "median_s", "min_s", "max_s", "paused", "est_s", "runs_s"]

# ---------- shared state (worker thread writes, window reads) ----------
lock = threading.Lock()
results = {}            # (w,h,steps,procs) -> dict(median, est, paused)
latest_lines = []       # text lines for the "latest results" box
state = dict(paused=False, stop=False, finished=False, idx=0, rep=0, cur=None,
             cur_start=0.0, cur_paused_total=0.0, pause_began=None, proc=None, note="")

if os.path.isfile(csv_path):                                  # resume
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            k = (int(r["width"]), int(r["height"]), int(r["steps"]), int(r["processors"]))
            results[k] = dict(median=float(r["median_s"]), est=float(r["est_s"]), paused=r["paused"] == "1")
else:
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerow(HEADER)
if not os.path.isfile(txt_path):
    with open(txt_path, "w") as f:
        f.write(f"Mandelbrot scaling benchmark | program: {program}\n")
        f.write(f"window: YMAX={YMAX} YMIN={YMIN} XMAX={XMAX} XMIN={XMIN} | runs per setting: {reps} (median shown)\n")
        f.write("order: theoretical quickest -> longest | time = whole program, start to finish, no plot window\n")
        f.write("'est' = the cost-model guess; 'P' = you paused during one of the runs (time excludes the pause)\n\n")
        f.write(f"{'size':>11} {'steps':>6} {'procs':>6} {'median s':>10} {'min s':>9} {'max s':>9} {'est s':>8}   all runs\n")

# ---------- one run of your program, pausable ----------
def run_once(w, h, steps, procs):
    answers = "\n".join(str(v) for v in
        [YMAX, YMIN, XMAX, XMIN, w, h, steps, COLOUR_CHOICE, procs]) + "\n"
    env = dict(os.environ, MPLBACKEND="Agg")                  # no window: plt.show() does nothing
    p = subprocess.Popen([sys.executable, program], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True, env=env, start_new_session=True)
    p.stdin.write(answers); p.stdin.close()
    with lock:
        state.update(proc=p, cur_start=time.perf_counter(), cur_paused_total=0.0, pause_began=None)
    was_paused = False
    while p.poll() is None:
        if state["stop"]:
            os.killpg(p.pid, signal.SIGKILL); p.wait(); return None, was_paused
        if state["paused"] and state["pause_began"] is None:
            os.killpg(p.pid, signal.SIGSTOP); state["pause_began"] = time.perf_counter(); was_paused = True
        elif not state["paused"] and state["pause_began"] is not None:
            os.killpg(p.pid, signal.SIGCONT)
            state["cur_paused_total"] += time.perf_counter() - state["pause_began"]; state["pause_began"] = None
        time.sleep(0.1)
    end = time.perf_counter()
    if state["pause_began"] is not None:                      # finished right as we paused
        state["cur_paused_total"] += end - state["pause_began"]; state["pause_began"] = None
    err = p.stderr.read()
    state["proc"] = None
    if p.returncode != 0:
        state["note"] = "program crashed: " + err.strip().splitlines()[-1][:80] if err.strip() else "program crashed"
        return None, was_paused
    return end - state["cur_start"] - state["cur_paused_total"], was_paused

def wait_if_paused():
    while state["paused"] and not state["stop"]:
        time.sleep(0.2)

def worker():
    for idx, key in enumerate(plan):
        if state["stop"]: return
        with lock: state["idx"] = idx; state["cur"] = key; state["rep"] = 0
        if key in results: continue
        times, any_pause = [], False
        for r in range(reps):
            wait_if_paused()
            if state["stop"]: return
            with lock: state["rep"] = r + 1
            dt, was_p = run_once(*key)
            if dt is None:
                if not state["stop"]: state["note"] = state["note"] or "a run failed, skipped"
                break
            times.append(dt); any_pause |= was_p
        if len(times) < reps: continue
        w, h, steps, procs = key
        med, lo, hi, est = statistics.median(times), min(times), max(times), estimate_seconds(*key)
        runs = ", ".join(f"{t:.2f}" for t in times)
        line = f"{w:>5}x{h:<5} {steps:>6} {procs:>6} {med:>10.2f} {lo:>9.2f} {hi:>9.2f} {est:>8.1f}   {runs}" + ("  P" if any_pause else "")
        with open(txt_path, "a") as f: f.write(line + "\n")
        with open(csv_path, "a", newline="") as f:
            csv.writer(f).writerow([w, h, steps, procs, f"{med:.3f}", f"{lo:.3f}", f"{hi:.3f}", int(any_pause), f"{est:.2f}", runs])
        with lock:
            results[key] = dict(median=med, est=est, paused=any_pause)
            latest_lines.append(f"{w}x{h} {steps}st {procs}p {med:.1f}s (est {est:.1f})")
    state["finished"] = True

# ---------- the window ----------
def fmt_time(sec):
    sec = int(sec); h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
    return f"{h} h {m:02d} min" if h else (f"{m} min {s:02d} s" if m else f"{s} s")

fig = plt.figure(figsize=(14, 8.2))
fig.canvas.manager.set_window_title("Mandelbrot scaling benchmark (live)") if hasattr(fig.canvas.manager, "set_window_title") else None
gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.78], left=0.06, right=0.985, top=0.92, bottom=0.08, wspace=0.28, hspace=0.34)
axes = {s: fig.add_subplot(gs[i // 2, i % 2]) for i, s in enumerate([50, 100, 150, 200])}
side = fig.add_subplot(gs[:, 2]); side.axis("off")
STYLE = {1: ("#4c4c4c", "o"), 2: ("#1f77b4", "s"), 4: ("#2ca02c", "^"), 8: ("#ff7f0e", "D"), 16: ("#d62728", "v")}
btn_ax_p, btn_ax_s = fig.add_axes([0.745, 0.012, 0.11, 0.05]), fig.add_axes([0.87, 0.012, 0.11, 0.05])
pause_btn, stop_btn = Button(btn_ax_p, "Pause"), Button(btn_ax_s, "Stop")
fig.suptitle("Time to finish vs image size, for each max-steps setting  (lines = number of processors)", fontsize=11)

def toggle_pause(_=None):
    state["paused"] = not state["paused"]
    pause_btn.label.set_text("Resume" if state["paused"] else "Pause")
    fig.canvas.draw_idle()
def stop(_=None):
    state["stop"] = True
    p = state["proc"]
    if p is not None:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
pause_btn.on_clicked(toggle_pause); stop_btn.on_clicked(stop)
fig.canvas.mpl_connect("key_press_event", lambda e: toggle_pause() if e.key == " " else None)
fig.canvas.mpl_connect("close_event", lambda e: stop())

def update(_=None):
    with lock:
        snap = dict(results); lines = list(latest_lines[-9:]); cur = state["cur"]; idx = state["idx"]; rep = state["rep"]
    for s, ax in axes.items():
        ax.clear()
        for p in procs_list:
            pts = sorted((w * h / 1e6, v["median"]) for (w, h, st, pp), v in snap.items() if st == s and pp == p)
            if pts:
                c, m = STYLE[p]
                ax.plot([x for x, _ in pts], [y for _, y in pts], marker=m, ms=4, lw=1.4, color=c, label=f"{p} proc")
        ax.set_xscale("log"); ax.set_yscale("log")
        plain = FuncFormatter(lambda v, _: f"{v:g}")
        ax.set_xlim(0.2, 70); ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20, 50]); ax.xaxis.set_minor_locator(LogLocator(subs=[], numticks=1))
        ax.xaxis.set_major_formatter(plain)
        ax.yaxis.set_major_formatter(plain); ax.yaxis.set_minor_locator(LogLocator(subs=[2, 5], numticks=12)); ax.yaxis.set_minor_formatter(plain)
        ax.set_title(f"{s} max steps", fontsize=10, loc="left")
        ax.set_xlabel("image size (million pixels)", fontsize=8); ax.set_ylabel("time (s)", fontsize=8)
        ax.tick_params(labelsize=8); ax.grid(alpha=0.25, lw=0.5)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    h_, l_ = axes[50].get_legend_handles_labels()
    if not h_:
        for p in procs_list:
            c, m = STYLE[p]; h_.append(plt.Line2D([], [], color=c, marker=m, ms=4, lw=1.4)); l_.append(f"{p} proc")
    axes[50].legend(h_, l_, fontsize=7, frameon=False, loc="upper left")
    # side panel
    side.clear(); side.axis("off")
    done_n = len(snap); total = len(plan)
    ratios = [v["median"] / v["est"] for v in snap.values() if v["est"] > 0]
    ratio = statistics.median(ratios) if ratios else 1.0
    remaining = sum(estimate_seconds(*k) * reps for k in plan if k not in snap) * ratio
    if state["finished"]: status, big = "ALL DONE", "#2ca02c"
    elif state["stop"]: status, big = "STOPPED (everything finished is saved)", "#d62728"
    elif state["paused"]: status, big = "PAUSED  (program frozen, clock stopped)", "#ff7f0e"
    else: status, big = "RUNNING", "#1f77b4"
    side.text(0, 1.0, status, fontsize=13, weight="bold", color=big, va="top", transform=side.transAxes)
    txt = f"settings done:  {done_n} / {total}\n"
    if cur and not state["finished"]:
        w, h, s, p = cur
        t0 = state["cur_start"]; pb = state["pause_began"]
        live = (time.perf_counter() - t0 - state["cur_paused_total"] - ((time.perf_counter() - pb) if pb else 0)) if state["proc"] else 0.0
        txt += f"\nnow running:\n  {w}x{h}, {s} steps,\n  {p} processors  (run {rep}/{reps})\n  this run so far: {live:5.1f} s\n  theory says:      {estimate_seconds(*cur):5.1f} s\n"
    txt += f"\nreal / theory so far:  {ratio:.2f}x\n(1.00x = theory is right)\n"
    txt += f"\ntime left (rough): {fmt_time(remaining)}\n"
    if state["note"]: txt += f"\nnote: {state['note']}\n"
    side.text(0, 0.90, txt, fontsize=9.5, va="top", family="monospace", transform=side.transAxes, linespacing=1.35)
    side.text(0, 0.34, "latest results (median):\n" + "\n".join(lines) if lines else "latest results:\n(waiting for the first one)",
              fontsize=8.5, va="top", family="monospace", transform=side.transAxes, linespacing=1.3)
    fig.canvas.draw_idle()

if __name__ == "__main__":
    print(f"{len(plan)} settings x {reps} runs, quickest first. Results go to {outdir}")
    print("Close the window or press Stop to stop safely.")
    th = threading.Thread(target=worker, daemon=True); th.start()
    timer = fig.canvas.new_timer(interval=500); timer.add_callback(update); timer.start()
    update()
    plt.show()                      # blocks until the window is closed
    if plt.get_backend().lower() == "agg":      # no window available (test mode): just wait for the run
        th.join(); update()
    state["stop"] = True; th.join(timeout=5)
    print("Saved in", outdir)
