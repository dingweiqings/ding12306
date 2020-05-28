class BussinessException(Exception):
      code=500
      message=''

      def __init__(self, code=500,message="Internal Server Error") -> None:
          super().__init__()
          self.code=code
          self.message=message

