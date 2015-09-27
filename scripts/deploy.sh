#!/bin/bash

if [[ $TRAVIS_BRANCH == 'gh-pages' ]] ; then

  git config user.name "yassineS"
  git config user.email "yassinesouilmi@gmail.com"

  git add .
  git commit -m "Deploy"


  #git remote add origin https://github.com/yassineS/yassines.github.io.git
  #git push origin master

  #git push --force --quiet "https://${git_user}:${git_password}@${git_target}" master:master > /dev/null 2>&1
  git push --force --quiet "https://${git_user}:${git_password}@${git_target}" $TRAVIS_BRANCH:master

else
  echo 'Invalid branch. You can only deploy from gh-pages.'
  exit 1
fi
