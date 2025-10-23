Download arXiv or inspirehep hosted papers using urls fetched from inspirehep page
PREREQUEST:
    pip install -r requirements.txt
STEP:
    1.find your papers to download in inspirehep.net
    2.press F12 to open devtools
    3.left-click on Elements tab
    4.left-click on the <head>...</head> tag
    5.right-click on the <head>...</head> tag and select "Edit as HTML"
    6.Ctrl+A then Ctrl+C copy the sources
    7.paste the source code into page.html(create one if not exist) in the same directory where arXivDownloader.py lies
    8.python arXivDownloader.py then drink some tea and wait
    9.Bingo! All finished right!