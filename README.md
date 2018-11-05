The goal of this project is to let users learn about hashtags they may have been confused about while using social media. I used the TagDef API, which crowdsources definitons of these hashtags (so they're not always very accurate). One aspect of my project that is different from what we have done in class is that I queried one database to see if data exists in it, and if it does, I got all info back on that specific user from another database, and displayed that info.
### Templates Provided:

* Custom errorhandler routes for 404 and 500 errors
* Custom error templates 404.html and 500.html
* Other templates:
    * `base.html` (the basis from which others inherit)
    * `name_form.html`(allows people to enter their names)
    * `name_example.html` (displays all names and ids)
    * `hashtag_form.html` (template that sends data to  TagDef API)
    * `hashtag_results.html` (displays API request results)
    * `hashtag_home.html`(layout for homepage)
    * `user_form.html`(template that allows person to input confusing Twitter user in order to see their saved hashtags)
    * `confusing_user.html` (displays confusing hashtags of given user (if any))
    * `all_hashtags.html` (displays all confusing users and confusing hashtags)

### View Functions Provided:
    * `/` (homepage w/ navigation to other pages)
    * `/hashtag_form' (renders hashtag form, makes call to TagDef API)
    * `/all_hashtags_and_users` (renders template to display all confusing hashtags and those who posted them)
    * `/find_hashtags_for_confuser_form` (renders template to input a certain user's confusing hashtags)
    * `/find_hashtags_for_confuser` (renders template displaying confusing user and their confusing hashtags)
    * `/name_form`(renders template for people to input their names))
    * `/names` (renders template to display all names stored in Name database)


