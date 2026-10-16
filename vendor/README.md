# Offline installation wheels

Unmodified universal Python wheels downloaded during project preparation:
- CustomTkinter 5.2.2 (MIT)
- darkdetect 0.8.0 (BSD 3-Clause)
- packaging 26.3 (Apache 2.0 / BSD 2-Clause)

The wheels retain upstream license/metadata files. Install using:
`python -m pip install --no-index --find-links vendor -r requirements.txt`.
Python 3.11+ and the platform's Tk runtime are separate prerequisites.
