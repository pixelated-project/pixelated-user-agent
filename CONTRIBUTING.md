# How to contribute

Here's the brief:

* We welcome contributions of all kinds, including but not limited to features, bug fixes, quality assurance, documentation, security review or asking questions
* Pull requests are based off, integrated into & rebased against master
* Write automated tests, ideally using TDD. CI needs to be green in order to merge.
* [Waffle](https://waffle.io/pixelated/pixelated-user-agent) board for ready to play work
* Contact us for questions & suggestions:
  * IRC: #pixelated @ chat.freenode.org ([join via webchat](https://webchat.freenode.net/))
  * Email: [team@pixelated-project.org](mailto:team@pixelated-project.org)
  * Twitter: [@pixelatedteam](https://twitter.com/pixelatedteam)


  This document outlines our way of working, gives hints and outlines the steps to make your contribution to Pixelated as smooth as possible. You're not required to read this before getting started. We're explaining the way we work to make sure you're having a good experience and can make best use of the time you're contributing to our project.

## Contributions steps

This is the lifecycle of a contribution. See our [README](README.md) for details on how to set up your development environment.

We follow a simplified fork + pull request workflow:

* To start, fork this repository and create a branch that's based off the latest commit in the `master` branch
* Implement the change
* Send a pull request against the master branch. Please make sure the automated tests are passing, as indicated by GitHub on the pull requests.
* Please keep your feature branch updated. Rebase your branch against upstream changes on the master branch, resolve any conflicts and make sure the tests are staying green.
* Your pull request will be reviewed and merged

### What to work on

Our [Kanban board "Waffle"](https://waffle.io/pixelated/pixelated-user-agent) provides an overview of issues that are ready to play or awaiting QA. If you're just getting familiar with Pixelated, see the [issues labeled 'Volunteer Task'](https://github.com/pixelated/pixelated-user-agent/labels/Volunteer%20task).

Generally, all issues that have no user assigned are awaiting work and free to play. If you want to make sure, or you think it will take more than a couple of days to complete your work, please reach out to us using the contact info above.

### Guidelines

When implementing your change, please follow this advice:

* Your change should be described in an issue, or latest in the pull request description.
* For bugs, please describe, in an issue or pull request:
  1. Steps to reproduce the behavior
  2. Expected behavior
  3. Actual behavior. Please also include as much meta-information as reasonable, e.g. time & date, software version etc.
* Pull requests need not to be finished work only; you can also submit changes in consecutive Pull Requests as long as CI stays green. Also, please send a PR with the intention of discussion & feedback. Please mark those Pull Requests appropriately.
* We review your pull request. This review is prioritised and done as part of our priotisation. During this time, we ask you to keep it up to date by frequently rebasing against master

### Review Criteria

When reviewing your contribution, we apply the following criteria:

* Test must be green. This usually includes an automatic check of the style guide using e.g. pep8 or jshint. All tests should be executed locally before you push, as well as on CI. If you struggle to reproduce a failure on CI locally, please notify us on IRC so we can resolve the issue.
* Your change should be in-line with Pixelated's direction. Chances that it is are good if, in descending priority:
  * It is described by an issue that is labelled as 'ready'
  * It is described by an issue that is labelled as 'backlog'
  * You've fixed a bug for which no issue existed yet, but described it in the pull request as explained in the section *Steps*
  * You've implemented a feature for which no issue existed yet. While we don't require up-front consensus, we strongly encourage you to describe feature suggestions in issues to get feedback before you spent significant time on implementation.
* We won't tolerate abusive, exploitative or harassing behavior in every context of our project and refuse collaboration with any individual who exposes such behavior.

## Types of contributions

Pixelated evolves upon the source code it's made of. This evolution is fueled by a variety of tasks; some of which require developing source code, some of which do not.

Contributions we appreciate:

* Features: New functionality is described in issues in the form of a user story to capture the end-user benefit.
* Bug fixes: Things go wrong from time to time.
* Quality Assurance: While every software change should be covered by automated tests, there are certain types of errors that are best spotted by a human. We apply QA to dev-complete changes.
* Documentation: Feedback & improvements of our guides & tutorial copywritings.
* Security review
* Translations
* Asking questions on IRC

## Translating UI

Anyone can contribute with Pixelated translating our user interface and making it accessible for more people. All the translation work is managed at [Transifex](https://www.transifex.com). Follow the steps below to start contributing:

* Sign up at [Transifex](https://www.transifex.com) and visit our [Pixelated project](https://www.transifex.com/pixelated/) page.
* On the project page, choose the language you want to work on. If the language doesn’t exist yet you can request a new language by clicking on the “Request language”.
* Then, click the “Join this Team” button to become a member of this team. You will be accepted as soon as possible.

We strongly recommend you read [Transifex User Guide](http://docs.transifex.com/) if it's the first time using this tool.

## ThoughtWorks' role

ThoughtWorks seeds the community that builds pixelated. We seed the development, investing our own resources: We provide a team of 10+ software delivery experts to lay the foundation for the project. We use our network and contacts to approach customers and users.

ThoughtWorks started building Pixelated because it is right. In combining our passion for defending a free internet and our capability to deliver software, we build software to counter widespread mass surveillance of email communication.

It is not ThoughWorks' goal to make money from Pixelated. The reasons are multiple, but at the end of the day, we believe that our goals of mass adoption and decentralization can best be achieved if Pixelated puts end users and providers before a revenue stream.
