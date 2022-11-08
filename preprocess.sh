#!/usr/bin/env bash

gsed -i -E 's#("[^"]*(url|href)":"https://(api\.github|avatars\.githubusercontent|github|uploads\.github)\.com/[^\\"]*",|,?"[^"]*(url|href)":"https://(api\.github|avatars\.githubusercontent|github|uploads\.github)\.com/[^\\"]*")##g' ~/github-data/2022-11-01-{0..23}.json
gsed -i "s/\\\u0000/\\\u0001/g" ~/github-data/2022-11-01-{0..23}.json
