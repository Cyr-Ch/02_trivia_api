import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://postgres:postgres@localhost:5432/"+self.database_name
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_paginate(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_paginate(self):
        response = self.client().get('/questions?page=1234')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], '404 not found')

    def test_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_category(self):
        response = self.client().get('/categories/120345')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], '404 not found')

    def test_delete_question(self):
        question = Question(question='Is there life on Mars', answer='YES',
                            difficulty=5, category=1)
        question.insert()
        question_id = question.id
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)
        question = Question.query.filter(
            Question.id == question.id).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_create_question(self):
        new_question = {
            'question': 'Is there life on Mars',
            'answer': 'YES',
            'difficulty': 5,
            'category': 1
        }
        total_questions_ = len(Question.query.all())
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        total_questions = len(Question.query.all())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions, total_questions_ + 1)

    def test_422_create_question(self):
        new_question = {
            'question': 'Is there life on Mars',
            'answer': 'YES',
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "422 unprocessable")

    def test_search(self):
        search = {'searchTerm': 'Sci'}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search(self):
        search = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404 not found")

    def test_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_questions_per_category(self):
        response = self.client().get('/categories/Food/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "404 not found")

    def test_play_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}}
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "422 unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()