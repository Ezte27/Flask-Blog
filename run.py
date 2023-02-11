from flaskBlog import app

# # Creating the database
# app.app_context().push()
# db.create_all()

if __name__ == '__main__':

    app.run(debug=True)
