# Hall-Of-Fame [![](https://img.shields.io/github/release/sourcerer-io/hall-of-fame.svg?colorB=58839b)](https://github.com/sourcerer-io/hall-of-fame/releases) [![](https://img.shields.io/github/license/sourcerer-io/hall-of-fame.svg?colorB=ff0000)](https://github.com/sourcerer-io/hall-of-fame/blob/master/LICENSE.md)

<img src="https://user-images.githubusercontent.com/20287615/43668986-d98186cc-9734-11e8-9c3e-3956a512be04.png" width="680px">

Hall-of-fame helps you show some love to your contributors. It automatically highlights your new, trending, and top contributors, and updates every hour. You can put this widget anywhere inside your README, e.g. to the "Contributing" section. No maintenance is required.

## How it works

Every hour, Hall-of-fame looks into recent commits of your repo using GitHub API. It then selects three categories of contributors: new (those who made their first commit to your repo in the last 7 days), trending (those with most commits in the last 7 days), and top (those with most commits of all time). It then selects up to three new contributors, up to 4 trending contributors, and if the total is less than 7, it fills up the remaining spots with top contributors.

Each contributor in the Hall-of-fame is represented with their avatar, and a badge new/trending/top with the corresponding number of commits. Each avatar links to a contributor's profile. This means that anyone has a chance to be prominently featured on your README for some time!

Hall-of-fame works with Sourcerer (https://sourcerer.io), but it's not required for your contributors. If a contributor has a Sourcerer profile, their Sourcerer avatar with a halo is used, and the avatar links to their Sourcerer profile. If they don't, an avatar based on their GitHub is used, and it is linked to their GitHub profile.

## Live examples

### [iterative/dvc](https://github.com/iterative/dvc)

[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/0)](https://sourcerer.io/fame/efiop/iterative/dvc/links/0)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/1)](https://sourcerer.io/fame/efiop/iterative/dvc/links/1)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/2)](https://sourcerer.io/fame/efiop/iterative/dvc/links/2)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/3)](https://sourcerer.io/fame/efiop/iterative/dvc/links/3)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/4)](https://sourcerer.io/fame/efiop/iterative/dvc/links/4)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/5)](https://sourcerer.io/fame/efiop/iterative/dvc/links/5)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/6)](https://sourcerer.io/fame/efiop/iterative/dvc/links/6)
[![](https://sourcerer.io/fame/efiop/iterative/dvc/images/7)](https://sourcerer.io/fame/efiop/iterative/dvc/links/7)

### [ironmussa/Optimus](https://github.com/ironmussa/Optimus)

[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/0)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/0)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/1)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/1)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/2)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/2)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/3)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/3)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/4)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/4)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/5)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/5)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/6)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/6)
[![](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/images/7)](https://sourcerer.io/fame/FavioVazquez/ironmussa/Optimus/links/7)


### [epicmaxco/vuestic-admin](https://github.com/epicmaxco/vuestic-admin)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/0)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/0)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/1)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/1)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/2)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/2)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/3)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/3)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/4)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/4)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/5)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/5)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/6)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/6)
[![](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/images/7)](https://sourcerer.io/fame/yandzee/epicmaxco/vuestic-admin/links/7)

## Getting started

Hall-of-fame code is entirely open source. You can run it in Google cloud yourself but we already do it for you. In order to add Hall-of-fame to your repository:

1. Sign in to sourcerer.io with your GitHub: (https://sourcerer.io/start)
2. Go to Settings/Hall-of-fame (https://sourcerer.io/settings#hof)
3. Add your repository there.
4. You should see the code to insert in your README.md. It will look something like this:

```
[![](https://sourcerer.io/fame/$USER/$OWNER/$REPO/images/0)](https://sourcerer.io/fame/$USER/$OWNER/$REPO/links/0)

...

[![](https://sourcerer.io/fame/$USER/$OWNER/$REPO/images/7)](https://sourcerer.io/fame/$USER/$OWNER/$REPO/links/7)
```
Paste that code into your README.md, and you should be good to go. Hall-of-fame will take care of the rest.

Note that Hall-of-fame will use your GitHub token for hourly updates via GitHub API. This will count towards your GitHub API limit. For a very large repo, you should expect a few dozen requests every hour, which is a small percentage of the 5,000 hourly limit that GitHub sets.

## FAQ

**Q:** Why do you only show 7 entries?

**A:** 7 is a lucky number. But seriously, recognition means that you stand out. It's hard to stand out in a crowd, so we limit to 7. If you strongly feel a different number is better, file an issue. We'll consider it.

**Q:** What is the reason to show new, trending, top, in this order?

**A:** We want Hall-of-fame to change frequently (hence emphasis on changes in the last week), and we want it to be immediately exciting for your first-time contributors. You need new contributors, right? We better make them excited.

**Q:** I just committed, and I don't see my face on Hall-of-fame! What is going on?

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
