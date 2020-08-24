# Sales Prediction

- Weekly movie data **annual_mojo_weekly_full.csv** (including weekend gross): scraped from here https://www.boxofficemojo.com/year/:
<img src="movie-data.png" width="80%" height="80%">

- Index reddit data with **Elasticsearch** discussing these movies: from here https://files.pushshift.io/reddit/
  - cd reddit_data
  - python create_index.py <index_name>
  
 - Download sentiment dictionary for feature extraction, e.g., **Subjectivity Lexicon**: from here http://mpqa.cs.pitt.edu/#subj_lexicon
 
 


