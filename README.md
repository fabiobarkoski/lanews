# lanews
News extractor from [latimes](https://www.latimes.com/)

## Installation

To use, install one of the following options:
- [rcc cli](https://github.com/robocorp/rcc?tab=readme-ov-file#getting-started)
- [robocorp vscode extensions](https://robocorp.com/docs/visual-studio-code)
- [robocorp cloud](https://robocorp.com/docs/courses/beginners-course-python/12-running-in-robocorp-cloud)

## Usage

To use locally, just change the work-items.json, insert the phrase that you want to search, also specify the topics and months, for example:
```json
{
  "payload": {
    "phrase": "lakers",
    "period": 2,
    "topics": ["sports"]
  },
  "files": {}
}
```
IMPORTANT: if you don't want to specify a topic, just leave an empty array in the topics.

This will search `lakers` on `sports` topic and get the latest 2 months of news. After will save in the `/output` dir an `output.xlsx` file and a pictures dir that contains all extracted data, like:
- title
- description
- date
- picture
- count of search phrases in the title and description
- if the title or description contains any amount of money

Then run following the instructions of your installation option :)

## Quality Code
To ensure a quality code run pre-commit before making a PR. Install the pre-commit on your environment or create an environment and install it. After, run:
```bash
pre-commit run --all-files
```
