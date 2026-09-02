import argparse
import sys
from pathlib import Path

from . import integrate as integrate_mod, preflight, reap as reap_mod, run as run_mod, status as status_mod
from .kata import KataClient
from .state import Paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kata-dispatch", description="parallel headless agents over a kata backlog")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--repo", default=".", help="primary checkout (default: cwd)")

    p = sub.add_parser("plan", help="show predicted surfaces for ready issues"); common(p)
    p.add_argument("--issues", nargs="*")
    p = sub.add_parser("run", help="dispatch workers"); common(p)
    p.add_argument("--agents", type=int, default=4); p.add_argument("--cap", type=int, default=8)
    p.add_argument("--model", default="opus"); p.add_argument("--budget-usd", type=float, default=25.0)
    p.add_argument("--no-gate", action="store_true"); p.add_argument("--gate-model", default="opus")
    p.add_argument("--poll", type=float, default=15.0); p.add_argument("--issues", nargs="*")
    p.add_argument("--no-systemd", action="store_true"); p.add_argument("--stall-action", choices=["report", "kill"], default="report")
    p.add_argument("--run-id")
    p = sub.add_parser("status", help="agents, branches, last commit, idle"); common(p)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("reap", help="clean up dead workers and stale locks"); common(p)
    p = sub.add_parser("preflight", help="exit 2 unless cwd is a dispatch worktree")
    p.add_argument("--hook", action="store_true")
    p = sub.add_parser("integrate", help="rebase integration onto main, run tests, ff main"); common(p)
    p.add_argument("--test-cmd", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "preflight":
        return preflight.main(["--hook"] if a.hook else [])
    paths = Paths(Path(a.repo))
    kata = KataClient(paths.repo)
    if a.cmd == "plan":
        print(run_mod.plan(paths, kata, a.issues)); return 0
    if a.cmd == "run":
        opts = run_mod.Options(agents=a.agents, cap=a.cap, model=a.model, budget_usd=a.budget_usd, gate=not a.no_gate,
                               gate_model=a.gate_model, poll_s=a.poll, issues=a.issues, use_systemd=not a.no_systemd,
                               stall_action=a.stall_action, run_id=a.run_id)
        recs = run_mod.run(paths, kata, opts)
        for r in recs:
            print(f"{r.ref}: {r.state} — {r.outcome} {r.merge_commit}")
        return 0
    if a.cmd == "status":
        rs = status_mod.rows(paths)
        if a.json:
            import json; print(json.dumps([r.__dict__ for r in rs], indent=1))
        else:
            print(status_mod.render(rs))
        return 0
    if a.cmd == "reap":
        for line in reap_mod.reap(paths, kata) or ["nothing to reap"]:
            print(line)
        return 0
    if a.cmd == "integrate":
        ok, msg = integrate_mod.integrate(paths, a.test_cmd)
        print(msg)
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
