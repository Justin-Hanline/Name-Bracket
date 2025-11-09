# Name-Bracket
What it is: 30-Name Round Robin
The code opens a window where the ranks and voting are available.

#What to Change
## To change what items are being voted on:
1) Open Names.py
2) Go to line 9 (where the list of names is declared) and change the names
3) Everything else should change automatically. If not, let me know so I can change it.

## To change the majority requirement & total voting requirements (all in BracketGUI.py):
1) Total votes required: Lines 144 & 168 (Default value: >=5)
2) Majority vote required: Line 152 (Default value: >=3)
3) Voting header: Line 251 (Default value: "First to 5 votes wins!")
These do not reset upon stat reset.

##Miscellanous:
1) To change what's displayed when being run, open BracketGUI.py and go to line 213. Change the text to what you want it to be.

## To run:
1) Open command prompt and change the directory to the folder where these files are being held (cd "FILE_DIRECTORY")
2) type "python BracketGUI.py"
Everything should compile accordingly

## An important comment about the timer:
1) To change the initial timer value, go to line 346 in BracketGUI.py and change the value
2) If you choose to set your initial timer value to less than 60 seconds, the image will skip Wartortle* and go straight to Blastoise* at the 30 second mark

*Assumes you don't change the files (the lines to change the names of these files are at lines 353, 355, and 357, so long you add the actual files to the folder.
