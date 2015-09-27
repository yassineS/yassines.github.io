#!/bin/bash

if [[ $TRAVIS_BRANCH == 'gh-pages' ]] ; then
  cd _site
  git init

  git config user.name "yassineS"
  git config user.email "yassinesouilmi@gmail.com"

  git add .
  git commit -m "Deploy"


  git remote add origin https://github.com/yassineS/yassines.github.io.git
  git push origin master
else
  echo 'Invalid branch. You can only deploy from gh-pages.'
  exit 1
fi
