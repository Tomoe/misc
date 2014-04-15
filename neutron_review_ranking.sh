#!/bin/sh
set -e

[ $# = 1 ] || {
  echo "Usage: $0 <reiewer's name>"
  exit
}

reviewer=$1

curl http://russellbryant.net/openstack-stats/neutron-reviewers-90.txt 2>/dev/null | \
    awk -F '|' -v reviewer=$reviewer '
BEGIN {
  i=-5;  # offset for discounting the header lines
};

{i++}

/Reviewer/{print  } # print the header

$2 ~ reviewer {
  print $0;
  print $2 " is at " ordinal(i)  " place" ;exit}

function ordinal(num){
  switch(num){
    case "11":
      suffix="th"
      break;
    case "12":
      suffix="th"
      break;
    case "13":
      suffix="th"
      break;
  }
  switch(num % 10) {
    case 1:
        suffix="st"
        break;
    case 2:
        suffix="nd"
        break;
    case 3: suffix="rd"
  }

  if (num >=11 && num <= 13){
    suffix="th"
  }
  return num  suffix
}
'



