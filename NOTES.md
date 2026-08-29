Q1:

I stripped whitespaces , converted empty values or strings to NULL.
I ALSO NORMALIZAED THE DATA , for example September 9, 2019 was converted to 2019-09-09 [ISO FORMAT]. 

I did this to have a consistent values and later for comparisons as well.

Q2:

I made the schema in a way where i put countries and generes in different tables,  Because a title can belong to many countries.
so the title-countries and title_generes had many to many relationship.

Q3: 

SInce I never worked with RAG, so i took a lot of help from AI
I had two options either put it in chunks or either take it as whole.
So to keep it simpler and the titles were lso small, there wasnt some larger strings kind of things. SO I decided to take it as whole.

I used the `all-MiniLM-L6-v2` Sentence Transformers model because it was suggested by AI and also i was searching for free model.
So it was showing that it can work for free for rought 6200 rows.

Q4:

The scale would increase, so i feel the time will be longer to run, cause when i was running tests n all, it was taking little time for few seconds to work for 6200 rows, For 100,000 titles the time and memory usage both will increase.

q5:
NOT GONNA LIE, 
I used ChatGPT throughout the assignment because Python and RAG were new technologies for me.
I used AI to make me understand the assignment , how i need the flow, i related it to my esg project [discussed in screening] a little that how i want the response with gemni.

The AI was suggesting me the wrong gemnin model which was no longer in use , then i used the 3.5 flash.
To be honest, my simple goal was to do this assignment but with learning.

How much i can learn while making this assignment in a smaller time frame.

q6:

With another four hours, I would focus on improving my current code only, cause i feel it miught not be the best assignment, as i was not familiar with any of this. LEARN MORE ABOUT IT, AND KEEP THE CODE IMPROVING.
