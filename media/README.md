# Workflow animation and token diagram

Open `index.html` to view the MP4 with automatic looping and playback controls. The GIF also repeats indefinitely. MP4 files rely on the player's loop setting; looping is enabled in the included HTML player. The animation has no audio; English captions and on-screen labels describe every phase.

- `logging-daily-weekly.mp4`: 40 seconds, 1280 × 800, 15 fps, H.264.
- `logging-daily-weekly.gif`: 40-second infinite loop, 960 × 600, 5 fps.
- `project-token-distribution.png`: six projects and six example models, 1600 × 1150.
- `example-token-data.csv`: editable illustrative weekly values, in tokens.
- `animation-storyboard.png`: five-scene preview.
- `animation-poster.png`: full-size first frame for the player.
- `workflow-captions.vtt`: English captions.
- `render_media.py`: editable source for the video, GIF and diagram.

The sample week totals 4,100,000 agent tokens. The model names are illustrative labels, not recommendations. Training/evaluation project usage covers agent calls; dataset training tokens and infrastructure spend are separate. None of these values comes from collected personal account activity.

Research & planning and Data analysis each use 1.10M tokens, followed by Software development (800k), Training & evaluation (600k), Prototyping (300k), and Reports & presentations (200k). GPT-6-Astra, GPT-6.1-Sol, Claude Sonnet5.5, and Claude Opus5.5 are the requested hosted-model labels. Only the Prototyping row uses self-hosted Qwen and Kimi.

Self-hosted model references checked 2026-10-21: [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), a deployment-friendly variant in the current Qwen3.8 generation, and [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3). These links document weights and serving; this illustration does not deploy either model or assert that either fits on a personal workstation.

## Re-render

Use Python 3 with `Pillow` and `imageio-ffmpeg` installed, then run `python media/render_media.py` from the repository root. The script uses Segoe UI fonts from `C:/Windows/Fonts`; on another OS, update the font path and font filenames. Example data is defined in `MODELS`, `PROJECTS`, `VALUES`, and `DAYS`; the CSV is generated from those values. Keep the daily and weekly totals consistent when changing them.

The panels show Linux, cloud, and Windows. Deployment arrows point from Linux to cloud; returning cloud usage logs point back to Linux, then onward to Windows. Windows initiates the pull from Linux; Linux initiates the pull from cloud. Large training data does not travel with the bundles.

The five scenes show Linux code editing and test runs; cloud deployment, preprocessing, training and evaluation; usage collection from `.claude` and `.codex`; daily project totals; and weekly analysis. Windows cycles through planning, presentation creation, email received/sent, and dashboard review throughout the loop. All code, test results, job metrics, and mail activity are simulated visual examples, not executed actions.

Local `.claude`/`.codex` data is a proposed collection source for the installed agent clients. Validate paths, formats, and usage fields for each client/version. Parse only available usage records; do not transfer credentials or entire configuration directories. These folders do not establish coverage for every consumer chat application.
