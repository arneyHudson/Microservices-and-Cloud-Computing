from models import PlayerModel

class PlayerService:
    def __init__(self):
        self.model = PlayerModel()

    def create(self, params):
        self.model.create(params)
        return {"message": "Player created successfully"}

    def list(self):
        return self.model.list()
    
    def delete(self, item_id):
       return self.model.delete(item_id)
   
    def get_by_id(self, item_id):
       response = self.model.get_by_id(item_id)
       return response
   
    def update(self, item_id, params):
       return self.model.update(item_id, params)
