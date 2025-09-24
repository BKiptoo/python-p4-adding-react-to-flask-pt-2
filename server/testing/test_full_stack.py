import pytest
import json
import requests
from app import app, db, Movie

class TestFlaskApp:
    """Test suite for Flask API"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                # Add test data
                test_movie = Movie(title="Test Movie")
                db.session.add(test_movie)
                db.session.commit()
                yield client
                db.drop_all()
    
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
    
    def test_movies_post_not_allowed(self, client):
        """Test POST /movies returns 405 Method Not Allowed"""
        response = client.post('/movies')
        assert response.status_code == 405
    
    def test_movie_model(self):
        """Test Movie model creation"""
        movie = Movie(title="Test Movie Title")
        assert movie.title == "Test Movie Title"
        assert str(movie) == "<Movie Test Movie Title>"


class TestLiveServers:
    """Test live Flask and React servers"""
    
    def test_flask_server_running(self):
        """Test Flask server is running and accessible"""
        try:
            response = requests.get('http://127.0.0.1:5555/movies', timeout=5)
            assert response.status_code == 200
            assert response.headers['content-type'] == 'application/json'
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert all('id' in movie and 'title' in movie for movie in data)
            print(f"✅ Flask API returned {len(data)} movies")
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Flask server is not running on port 5555")
    
    def test_react_server_running(self):
        """Test React server is running and serving HTML"""
        try:
            response = requests.get('http://localhost:4000', timeout=5)
            assert response.status_code == 200
            assert 'text/html' in response.headers['content-type']
            assert 'React App' in response.text
            print("✅ React server is serving HTML")
            
        except requests.exceptions.ConnectionError:
            pytest.fail("React server is not running on port 4000")
    
    def test_proxy_functionality(self):
        """Test React proxy forwards requests to Flask"""
        try:
            # Get data directly from Flask
            flask_response = requests.get('http://127.0.0.1:5555/movies', timeout=5)
            flask_data = flask_response.json()
            
            # Get data through React proxy
            proxy_response = requests.get('http://localhost:4000/movies', timeout=5)
            proxy_data = proxy_response.json()
            
            # Data should be identical
            assert flask_data == proxy_data
            assert len(flask_data) == len(proxy_data)
            print(f"✅ Proxy working: {len(proxy_data)} movies returned through both routes")
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Either Flask or React server is not running")
    
    def test_cors_headers(self):
        """Test CORS headers are set correctly"""
        try:
            response = requests.get('http://127.0.0.1:5555/movies', timeout=5)
            assert 'Access-Control-Allow-Origin' in response.headers
            assert response.headers['Access-Control-Allow-Origin'] == '*'
            print("✅ CORS headers are properly configured")
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Flask server is not running")
    
    def test_database_populated(self):
        """Test database has been seeded with data"""
        try:
            response = requests.get('http://127.0.0.1:5555/movies', timeout=5)
            data = response.json()
            
            # Should have 50 movies from seed.py
            assert len(data) == 50
            
            # Verify structure of first movie
            first_movie = data[0]
            assert isinstance(first_movie['id'], int)
            assert isinstance(first_movie['title'], str)
            assert len(first_movie['title']) > 0
            
            print(f"✅ Database properly seeded with {len(data)} movies")
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Flask server is not running")


class TestConfiguration:
    """Test application configuration"""
    
    def test_package_json_proxy(self):
        """Test React package.json has correct proxy configuration"""
        with open('client/package.json', 'r') as f:
            package_data = json.load(f)
        
        assert 'proxy' in package_data
        assert package_data['proxy'] == 'http://127.0.0.1:5555'
        assert package_data['scripts']['start'] == 'PORT=4000 react-scripts start'
        print("✅ React package.json correctly configured")
    
    def test_procfile_configuration(self):
        """Test Procfile.dev is configured correctly"""
        with open('Procfile.dev', 'r') as f:
            content = f.read()
        
        assert 'web: PORT=4000 npm start --prefix client' in content
        assert 'api: gunicorn -b 127.0.0.1:5555 --chdir ./server app:app' in content
        print("✅ Procfile.dev correctly configured")
    
    def test_flask_app_structure(self):
        """Test Flask app has correct structure"""
        # Test imports work
        from app import app, db, Movie
        
        # Test app configuration
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///app.db'
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
        assert app.json.compact == False
        
        print("✅ Flask app structure is correct")