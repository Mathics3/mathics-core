<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Overview](#overview)
- [Issues and Issue Fixers, Priorities](#issues-and-issue-fixers-priorities)
- [What to report](#what-to-report)
- [Environment](#environment)
- [Narrowing the problem](#narrowing-the-problem)
- [Questions, User Environment and Installation](#questions-user-environment-and-installation)
- [Karma](#karma)

<!-- markdown-toc end -->

# Overview

Reporting bugs in a thoughtful way is helpful.

However any project that attempts to mimic the Wolfram Language is going fall short. It is easy to find in a matter of minutes some built-in function Mathics doesn't implement but is in WL. Or that is implemented but doesn't match WL.


# Issues and Issue Fixers, Priorities

Right now, there are more issues in the queue to keep issue fixers busy indefinitely. And everyone fixing bugs is essentially doing this on a voluntary basis.

Therefore helpful to priorities the kinds of issues. Things that are helpful in determining priorities:

* Is this a bug or feature that has no workaround?
* Is this bug of feature blocking something important?
* What is the impact of this bug on the entire community?

# What to report

The basic requirement is pretty simple:

* What you entered
* What you got back
* What you expected to get back
* Have you tried anything to work solve or around the problem?

Most of the time people will report an error message or a Python traceback without any context. Remember to give what was _entered_ the entire output of what you got back.
But you may think, _all_ of the input and _all_ of the output is rather long, and I know that isn't useful.

A couple things here, if you know what the problem is then, consider putting in a [Github Pull Request](https://www.digitalocean.com/community/tutorials/how-to-create-a-pull-request-on-github) to fix the problem.

Also if the input and output is large to narrow the problem into the smallest case that exhibits the problem. See below.

# Environment

We have arranged the command-line interfaces to report what versions of software they use on entry. So if a command-line interface was used and you follow the basic steps in "What to report" included in "What you got back" will be environment information. If you are using the Django interface there is an "about" page (http://localhost:8000/about) which lists versions of software


# Narrowing the problem

Often when you encounter a bug or problem, you are in the middle of some other involved task for which this a part of.

But when reporting a problem, it is helpful to report the smallest case that exhibits the problem.

Here is an example excerpted from a real bug report:

```
Hi, I saw wrong values while calculating a flight dynamics problem. Here is the code:

A=7.17;
e=0.9;
Clw=0.71;
Xcg=0.591;
Xca=0.50075;
N0=0.94141;
at=4.15;
aw=4.02;
St=4.06;
Sw=21.3;
w=2200;
Lt=6;
... 80 lines omitted
CmdTita = -1.1atVrednt*(Lt-Xa)/(cam*mu)


This is the system:

DL={{Cd+lambda, (Cdalfa-Clw)/2, Clw/2},{Clw, Clalfa/2+lambda, -lambda},{0,Cmalfa+Cmdalfalambda,CmdTitalambda-2lambda^2Kyy^2/(cam^2*mu)}};

Here resolution:
```

This kind of thing is too long and complex or us to handle.

# Questions, User Environment and Installation

Many people will use the issue tracker as a means to solicit help for a problem that they have, or to get help on how to set up Mathics. Judgement should be used here.

If the problem is of a more general nature consider other channels like [StackOverflow](https://stackoverflow.com/) or [Mathematica & Wolfram Language](https://mathematica.stackexchange.com/).

# Karma

We realize that following the instructions given herein puts a bit of burden on the bug reporter. This is justified since it attempts to balance the burden and effort needed to fix the bug with the amount of effort to report the problem. And it attempts to balance number of would-be bug reporters with the number of bug fixers. Better bug reporters are more likely to move in the category of bug fixers.

We  may take into consideration is the bug reporter's karma.

* Have you demonstrably contributed to open source? I may look at your github profile to see what contributions you have made, how popular those contributions are, or how popular you are.
* How appreciative are you? Have you starred this project that you are seeking help from? Have you starred _any_ github project? And the above two kind of feed into ...
* Attitude. Some people feel that they are doing the world a great favor by just pointing out that there is a problem whose solution would greatly benefit them. (This might account partially
  for the fact that those that have this attitude often don't read or follow instructions such as those given here.)
