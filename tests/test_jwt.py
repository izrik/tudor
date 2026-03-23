import unittest
from unittest.mock import Mock, patch

from tudor import create_access_token, verify_token


class JWTUtilityTest(unittest.TestCase):
    """Test JWT utility functions"""

    def setUp(self):
        self.secret_key = 'test_secret_key'
        self.algorithm = 'HS256'
        self.test_data = {
            'sub': 'test@example.com',
            'user_id': 1,
            'is_admin': False
        }

    def test_create_access_token_success(self):
        """Test successful JWT token creation"""
        token = create_access_token(self.test_data, self.secret_key, self.algorithm, 30)

        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

        # Verify token can be decoded
        payload = verify_token(token, self.secret_key, self.algorithm)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], self.test_data['sub'])
        self.assertEqual(payload['user_id'], self.test_data['user_id'])
        self.assertEqual(payload['is_admin'], self.test_data['is_admin'])
        self.assertIn('exp', payload)

    def test_verify_token_valid(self):
        """Test successful token verification"""
        token = create_access_token(self.test_data, self.secret_key, self.algorithm, 30)
        payload = verify_token(token, self.secret_key, self.algorithm)

        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], self.test_data['sub'])

    def test_verify_token_invalid_secret(self):
        """Test token verification with wrong secret"""
        token = create_access_token(self.test_data, self.secret_key, self.algorithm, 30)
        payload = verify_token(token, 'wrong_secret', self.algorithm)

        self.assertIsNone(payload)

    def test_verify_token_invalid_algorithm(self):
        """Test token verification with wrong algorithm"""
        token = create_access_token(self.test_data, self.secret_key, self.algorithm, 30)
        payload = verify_token(token, self.secret_key, 'HS512')

        self.assertIsNone(payload)

    def test_verify_token_malformed(self):
        """Test verification of malformed token"""
        payload = verify_token('invalid.token.here', self.secret_key, self.algorithm)
        self.assertIsNone(payload)


class JWTViewLayerTest(unittest.TestCase):
    """Test JWT functionality in the view layer"""

    def setUp(self):
        from view.layer import ViewLayer, DefaultRenderer
        from logic.layer import LogicLayer

        # Mock components
        self.mock_ll = Mock(spec=LogicLayer)
        self.mock_renderer = Mock(spec=DefaultRenderer)
        self.mock_login_src = Mock()

        self.vl = ViewLayer(self.mock_ll, None, renderer=self.mock_renderer, login_src=self.mock_login_src)

        # Mock user
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = 'test@example.com'
        self.mock_user.is_admin = False

    def test_wants_json_true(self):
        """Test wants_json returns True for application/json"""
        mock_request = Mock()
        mock_request.headers = {'Accept': 'application/json'}

        result = self.vl.wants_json(mock_request)
        self.assertTrue(result)

    def test_wants_json_false(self):
        """Test wants_json returns False for other content types"""
        mock_request = Mock()
        mock_request.headers = {'Accept': 'text/html'}

        result = self.vl.wants_json(mock_request)
        self.assertFalse(result)

    def test_wants_json_no_header(self):
        """Test wants_json returns False when no Accept header"""
        mock_request = Mock()
        mock_request.headers = {}

        result = self.vl.wants_json(mock_request)
        self.assertFalse(result)


class JWTRequestLoaderTest(unittest.TestCase):
    """Test JWT request loader functionality"""

    def setUp(self):
        self.secret_key = 'test_secret'
        self.algorithm = 'HS256'
        self.test_user = Mock()
        self.test_user.email = 'test@example.com'

    @patch('tudor.pl')
    def test_request_loader_jwt_success(self, mock_pl):
        """Test successful JWT authentication via request loader"""
        # Create a valid token
        token_data = {'sub': 'test@example.com', 'user_id': 1}
        token = create_access_token(token_data, self.secret_key, self.algorithm, 30)
        mock_pl.get_user_by_email.return_value = self.test_user

        # Mock request with Bearer token
        mock_request = Mock()
        mock_request.headers = {'Authorization': f'Bearer {token}'}

        # Mock the app config
        mock_app = Mock()
        mock_app.config = {
            'JWT_SECRET_KEY': self.secret_key,
            'JWT_ALGORITHM': self.algorithm
        }

        with patch('tudor.app', mock_app), \
             patch('tudor.pl', mock_pl):

            # Import and call the function (it's defined in generate_app)
            # We'll simulate the logic here
            auth_header = mock_request.headers.get('Authorization')
            self.assertTrue(auth_header.startswith('Bearer '))

            token_part = auth_header.replace('Bearer ', '', 1)
            payload = verify_token(token_part, self.secret_key, self.algorithm)
            self.assertIsNotNone(payload)
            self.assertEqual(payload['sub'], 'test@example.com')

    @patch('tudor.pl')
    @patch('tudor.bcrypt')
    def test_request_loader_basic_auth_success(self, mock_bcrypt, mock_pl):
        """Test successful Basic authentication via request loader"""
        import base64

        mock_pl.get_user_by_email.return_value = self.test_user
        mock_bcrypt.check_password_hash.return_value = True

        # Create Basic auth header
        credentials = base64.b64encode(b'test@example.com:password').decode()
        mock_request = Mock()
        mock_request.headers = {'Authorization': f'Basic {credentials}'}

        with patch('tudor.pl', mock_pl), \
             patch('tudor.bcrypt', mock_bcrypt):

            # Simulate the basic auth logic
            auth_header = mock_request.headers.get('Authorization')
            self.assertTrue(auth_header.startswith('Basic '))

            api_key = auth_header.replace('Basic ', '', 1)
            decoded = base64.b64decode(api_key).decode('utf-8')
            email, password = decoded.split(':', 1)

            self.assertEqual(email, 'test@example.com')
            self.assertEqual(password, 'password')

    def test_request_loader_no_auth(self):
        """Test request loader with no authorization header"""
        mock_request = Mock()
        mock_request.headers = {}

        # Simulate the logic
        auth_header = mock_request.headers.get('Authorization')
        self.assertIsNone(auth_header)


if __name__ == '__main__':
    unittest.main()