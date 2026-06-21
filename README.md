Draw a vrbo calendar from a vrbo Host's reservation calendar

Using the host's synchronization url the output is a png file that resembles the vrbo websites booking calendar 
The program run in cron will detect changes from the previous run and send the calendar again to an email or as mms to a phone to maid serices or maintenance personnell

Given a vrbo calendar url pull the calendar, draw the calender including reservations and blocks and then send them as an email attachment. 

install requirements file from requirements.txt <br>
  pip install -r requirements.txt

create a config.py with all the needed constants 

run the script 

