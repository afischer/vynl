<p><img src="http://i.imgur.com/HhAIJc8.png" align="middle"> <i>The Dankest DJ App in the Universe.</i> </p>
<p> Check us out at http://vynl.party </p>


-----



## Collaborators
|                                       |   **Member**   |                   **GitHub**                 |            **Role**            |
|---------------------------------------|:--------------:|:--------------------------------------------:|:------------------------------:|
| ![EC](http://i.imgur.com/NY22s6r.png) | Eric Z. Chen   |[`@ezchen`](https://github.com/ezchen)        | Frontend Javascript, API mgmt  |
| ![AF](http://i.imgur.com/a150nV8.png) | Andrew Fischer |[`@afischer`](https://github.com/afischer)    | Frontend Javascript, MVC mgmt  |
| ![DZ](http://i.imgur.com/f8pAznc.png) | Daniel Zabari  |[`@Zabari`](https://github.com/Zabari)        | Backend Python, Database Mgmt  |

## Timetable
See [TODO.md](https://github.com/afischer/vynl/blob/master/TODO.md) for a complete timeline and goal completion deadlines.

## Video
[![YTVideo](http://img.youtube.com/vi/BJfs_lFGRPo/0.jpg)](https://www.youtube.com/watch?v=RpIWkr_cYx8)



## Workflow

1. Branch from `dev` (use style initials-description for branch naming)
2. Make your changes. Commit a lot. Be descriptive in your commit messages.
3. Push your changes to your new branch. using `git push origin branch-name`
4. When finished, prepare to merge back into master.
    1. If you have made a lot of changes, consider doing a `git rebase` from master to avoid conflics
    2. If changes can be easily merged, make a PR from github. Assign it to **someone else**
5. Ask someone else to merge to `develop`. Have them do a code review
6. Merge to `develop`.
7. Make sure everything is okay and working properly. After a few hours/days, delete the stale branch.
  

After a number of changes have been made, `develop` will be merged into `master` and deployed to the server.
