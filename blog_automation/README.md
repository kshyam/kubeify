# Kubeify daily blog publishing

The publisher generates a post using OpenCode, checks prose length, FAQ, CTA and source URL availability, renders a Kubeify-coloured WebP banner, and commits and pushes only the two generated files to `origin/main`. The checks do not independently verify the article's factual claims; inspect the generated articles and their sources. A failed validation stops publishing. A failed push leaves `.pending.json` for retry on the next run.

Requires Python 3.9+ with Pillow, DejaVu fonts, an authenticated OpenCode CLI, a working GitHub SSH key, and a clean index. The default model is `opencode/big-pickle`. Set `OPENCODE_MODEL`, `OPENCODE_BIN`, or `KUBEIFY_BLOG_ENV_FILE` to override configuration. The wrapper sources `~/.config/kubeify/blog.env` if present; keep credentials out of Git.

Run manually with `bash blog_automation/cron_publish.sh`. Output is written to `blog_automation/blog.log` by cron. Topic selection uses `topics.json` and existing post slugs; after the pool is exhausted the model proposes a new title. It does not automatically research or rank current trends.

Cron uses the host timezone. On this machine the host timezone is IST; `0 10 * * *` runs daily at 10:00 IST. If the host timezone changes, update the schedule. Keep the machine on and the cron service running.
