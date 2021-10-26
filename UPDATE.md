# Personal note on how to push an update
1. Make new release on the right side of your repo in GitHub
2. Get the link for the tar.gz archive and paste in setup.py
3. Run the commands: ```python3 setup.py bdist_wheel
python3 -m twine upload dist/*```
4. Test: ```pip install ecdh --upgrade```