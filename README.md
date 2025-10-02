# Name-Bracket
What it is: 30-Name Round Robin
The code opens a window where the ranks and voting are available.

To change what items are being voted on:
1) Open Names.py
2) Go to line 9 (where the list of names is declared) and change the names
3) Everything else should change automatically. If not, let me know so I can change it.

To change the majority requirement & total voting requirements (all in BracketGUI.py):
1) Total votes required: Lines 141 & 164 (Default value: >=5)
2) Majority vote required: Line 149 (Default value: >=3)
3) Voting header: Line 248 (Default value: "First to 5 votes wins!")
These do not reset upon stat reset.

To run:
1) Open command prompt and change the directory to the folder where these files are being held (cd "FILE_DIRECTORY")
2) type "python BracketGUI.py"
Everything should compile accordingly
