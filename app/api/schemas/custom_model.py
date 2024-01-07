from pydantic import BaseModel


class CustomModel(BaseModel):
    def to_log(self):
        return self.model_dump(mode='json', exclude_none=True)
