# Hall-Of-Fame

<img src="https://user-images.githubusercontent.com/20287615/43668986-d98186cc-9734-11e8-9c3e-3956a512be04.png" width="680px">

Hall-of-fame helps you show some love to your contributors. It automatically highlights your new, trending, and top contributors, and updates every hour. You can put this widget anywhere inside your README, e.g. to "Contributing" section. No maintenance is required.

**Until Aug 24th only:** We'll be happy to make a pull request with hall-of-fame for your repo. Instructions: sign in to (https://sourcerer.io) with your GitHub (so that hall-of-fame could use your GitHub token to update), and send us an email to hello@sourcerer.io with the repo name. We'll take care of the rest.

## How it works

Every hour, Hall-of-fame looks into recent commits of your repo using GitHub API. It then selects three categories of contributors: new (those who made their first commit to your repo in the last 7 days), trending (those with most commits in the last 7 days), and top (those with most commits of all time). It then selects up to three new contributors, up to 4 trending contributors, and if total is less than 7, it fill up the remaining spots with top contributors.

Each contributor in the Hall-of-fame is represented with their avatar, and a badge new/trending/top with the corresponding number of commits. Each avatar links to a contributor's profile. Which means that anyone has a chance to be prominently featured on your README for some time!

Hall-of-fame works with Sourcerer (https://sourcerer.io), but it's not required for your contributors. If a contributor has a Sourcerer profile, their Sourcerer avatar with a halo is used, and the avatar links to their Sourcerer profile. If they don't, an avatar based on their GitHub is used, and it is linked to their GitHub profile.

## Getting started

Hall-of-fame code is entirely open source. You can run it in Google cloud yourself but we already do it for you. In order to add Hall-of-fame to your repository:

1. Sign in to sourcerer.io with your GitHub: (https://sourcerer.io/start)
2. Go to Settings/Hall-of-fame (https://sourcerer.io/settings#hof)
3. Add your repository there.
4. You should see code to insert in your README.md. It will look something like this:

```
[![](https://sourcerer.io/fame/$USER/$OWNER/$REPO/images/0)](https://sourcerer.io/fame/$USER/$OWNER/$REPO/links/0)

...

[![](https://sourcerer.io/fame/$USER/$OWNER/$REPO/images/7)](https://sourcerer.io/fame/$USER/$OWNER/$REPO/links/7)
```
Paste that code into your README.md, and you should be good to go. Hall-of-fame will take care of the rest.

Note that Hall-of-fame will use your GitHub token for hourly updates via GitHub API. This will count towards your GitHub API limit. For a very large repo, you shoud expect a few dozen requests every hour, which is a small percentage of 5,000 hourly limit that GitHub sets.

## FAQ

**Q:** Why do you only show 7 entries?

**A:** 7 is a lucky number. But seriously, recognition means that you stand out. It's hard to stand out in a crowd, so we limit to 7. If you strongly feel a different number is better, file an issue. We'll consider.

**Q:** What is the reason to show new, trending, top, in this order?

**A:** We want Hall-of-fame to change frequenty (hence emphasis on changes in the last week), and we want it to be immediately exciting for your first time contributors. You need new contributors, right? We better make them excited.

**Q:** I just commited, and I don't see my face on Hall-of-fame! What is going on?

**A:** It refreshes once an hour, and sometimes takes a bit longer. Just wait, it will be there. Another possibility is there are enough contributors with more commits this week. Contributors are sorted by the number of commits, so if you push another commit, you will increase your chance to show in Hall-of-fame.

## Contributing

Contribute to Hall-of-fame by all means. Here is the live Hall-of-fame for this repo:

[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/0)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/0)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/1)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/1)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/2)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/2)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/3)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/3)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/4)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/4)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/5)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/5)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/6)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/6)
[![](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/images/7)](https://sourcerer.io/fame/sergey48k/sourcerer-io/hall-of-fame/links/7)
