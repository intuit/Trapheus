
class IBaseProvider():

    def connect(self):
        """Connect to data source and manage connection"""
        pass

    def extract_data(self):
        """Extract/Transform data after quering the source"""
        pass

    def query(self):
        """Handle querying semantics for the source"""
        pass