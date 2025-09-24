import pytest
import json
import sys
import os

# Add server directory to path so we can import our app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db, Movie

class TestFlaskApp:
    """Unit tests for Flask application"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                # Add test data
                test_movie = Movie(title="Test Movie")
                db.session.add(test_movie)
                db.session.commit()
                yield client
    
    def test_movies_get_route(self, client):
        """Test GET /movies route returns JSON data"""
        response = client.get('/movies')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert 'id' in data[0]
        assert 'title' in data[0]
        assert data[0]['title'] == "Test Movie"
        print(f"✅ GET /movies returns {len(data)} movies with correct structure")
    
    def test_movies_post_not_allowed(self, client):
        """Test POST /movies returns 405 Method Not Allowed"""
        response = client.post('/movies')
        assert response.status_code == 405
        print("✅ POST /movies correctly returns 405 Method Not Allowed")
    
    def test_movies_put_not_allowed(self, client):
        """Test PUT /movies returns 405 Method Not Allowed"""
        response = client.put('/movies')
        assert response.status_code == 405
        print("✅ PUT /movies correctly returns 405 Method Not Allowed")
    
    def test_movies_delete_not_allowed(self, client):
        """Test DELETE /movies returns 405 Method Not Allowed"""
        response = client.delete('/movies')
        assert response.status_code == 405
        print("✅ DELETE /movies correctly returns 405 Method Not Allowed")
    
    def test_movie_model(self):
        """Test Movie model creation and methods"""
        movie = Movie(title="Test Movie Title")
        assert movie.title == "Test Movie Title"
        assert str(movie) == "<Movie Test Movie Title>"
        
        # Test to_dict method
        movie.id = 1
        movie_dict = movie.to_dict()
        assert movie_dict['id'] == 1
        assert movie_dict['title'] == "Test Movie Title"
        print("✅ Movie model works correctly with to_dict() method")
    
    def test_app_configuration(self):
        """Test Flask app configuration"""
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
        assert app.json.compact == False
        print("✅ Flask app configuration is correct")
    
    def test_cors_configured(self, client):
        """Test CORS headers are set"""
        response = client.get('/movies')
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        print("✅ CORS headers are properly configured")


class TestConfiguration:
    """Test application configuration files"""
    
    def test_package_json_exists_and_configured(self):
        """Test React package.json has correct proxy configuration"""
        package_path = os.path.join(os.path.dirname(__file__), '..', '..', 'client', 'package.json')
        assert os.path.exists(package_path), "client/package.json should exist"
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        assert 'proxy' in package_data
        assert package_data['proxy'] == 'http://127.0.0.1:5555'
        assert package_data['scripts']['start'] == 'PORT=4000 react-scripts start'
        print("✅ React package.json correctly configured")
    
    def test_procfile_exists_and_configured(self):
        """Test Procfile.dev is configured correctly"""
        procfile_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Procfile.dev')
        assert os.path.exists(procfile_path), "Procfile.dev should exist"
        
        with open(procfile_path, 'r') as f:
            content = f.read()
        
        assert 'web: PORT=4000 npm start --prefix client' in content
        assert 'api: gunicorn -b 127.0.0.1:5555 --chdir ./server app:app' in content
        print("✅ Procfile.dev correctly configured")
    
    def test_database_file_exists(self):
        """Test database file was created"""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'app.db')
        assert os.path.exists(db_path), "Database file should exist"
        
        # Check file size > 0 (has data)
        assert os.path.getsize(db_path) > 0, "Database file should contain data"
        print(f"✅ Database file exists and has data ({os.path.getsize(db_path)} bytes)")
    
    def test_react_app_js_updated(self):
        """Test React App.js has been updated with useEffect"""
        app_js_path = os.path.join(os.path.dirname(__file__), '..', '..', 'client', 'src', 'App.js')
        assert os.path.exists(app_js_path), "client/src/App.js should exist"
        
        with open(app_js_path, 'r') as f:
            content = f.read()
        
        assert 'useEffect' in content
        assert 'fetch("/movies")' in content
        assert 'console.log(movies)' in content
        assert 'Check the console for a list of movies!' in content
        print("✅ React App.js correctly updated with useEffect and fetch")


def test_codegrade_placeholder():
    """Original codegrade placeholder test"""
    assert 1 == 1
    print("✅ Codegrade placeholder test passes")