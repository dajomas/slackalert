to debug the slackalert python script do the following:
* rename slackalert.py to action_slackalert.py
* rename debug_slackalert.sh to slackalert.sh

Now, when the alert triggers the output is send to $SPLUNK_HOME/slackalert/tmp/slackalert.out


Once debugging is finished, rename the files back to their original filenames
