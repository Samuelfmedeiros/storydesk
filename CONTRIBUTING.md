# Contributing

Thanks for considering contributing to Storydesk!

## How to Contribute

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m "feat: description"`)
4. Push (`git push origin feat/my-feature`)
5. Open a Pull Request

## Dev setup

Zero dependencies — plain Python 3.10+ and the stdlib:

```bash
git clone https://github.com/Samuelfmedeiros/storydesk.git
cd storydesk
export PATH="$PWD/bin:$PATH"

# run the tests:
python3 -m unittest discover -s tests

# run the CLI straight from the repo:
./bin/storydesk --help
```

Editorial state (config, memory, daylog) lives in `~/.storydesk/` and never enters
the repo. To test in isolation, point `STORYDESK_HOME` at a temp directory.

## Code Style

- Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- Keep it simple — no speculative abstractions, no new dependencies
  (the project is 100% stdlib; a PR adding a runtime dependency needs a strong case)
- Tests must pass before opening the PR

## Adding an adapter

New blog backends implement the `ContentAdapter` interface from
`storydesk/adapter.py` (`init`, `draft_path`, `write_draft`, `list_slugs`, `build`,
`publish`; `verify_live` is already provided). Add the adapter under `adapters/`,
import it **absolutely** (`from storydesk.adapter import ContentAdapter`) and cover
it with tests.

## Report Issues

Bugs, ideas and adapter requests are welcome in the
[issue tracker](https://github.com/Samuelfmedeiros/storydesk/issues).

## License

By contributing you agree that your contributions are licensed under the MIT License.
