# app/fields.py
from app.exceptions import ValidationError

class Field:
    def __init__(self, primary_key: bool = False, null: bool = True, default=None, unique: bool = False):
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.unique = unique
        
        # Instantiated fields don't know their own names yet. 
        # Python will provide these automatically using __set_name__.
        self.name = None
        self.column_name = None

    def __set_name__(self, owner, name):
        """
        Automatically called by Python when the Model class is created.
        Example: If inside 'User', we have 'name = CharField()', 
        owner will be 'User' and name will be 'name'.
        """
        self.name = name
        self.column_name = name

    def __get__(self, instance, owner):
        """
        Called when you read the field: `print(user.name)`
        'instance' is the model object (e.g., user).
        'owner' is the model class (e.g., User).
        """
        # If accessing the descriptor directly from the class level (e.g., User.name), 
        # return the field instance itself.
        if instance is None:
            return self
        
        # Read directly from the instance's private data storage dictionary
        if not hasattr(instance, '_data'):
            instance._data = {}
            
        # Return the value if it exists, otherwise fall back to default
        return instance._data.get(self.name, self.default)

    def __set__(self, instance, value):
        """
        Called when you assign a value: `user.name = "Mouad"`
        """
        # 1. Enforce validation before saving anything
        self.validate(value)
        
        if not hasattr(instance, '_data'):
            instance._data = {}
            
        if not hasattr(instance, '_dirty'):
            instance._dirty = set()

        # 2. Track changes: If the value is changing, mark this field as "dirty"
        # This tells the ORM later exactly which columns need an UPDATE query.
        old_value = instance._data.get(self.name)
        if old_value != value:
            instance._dirty.add(self.name)

        # 3. Store the clean value directly inside the instance data dictionary
        instance._data[self.name] = value

    def validate(self, value):
        """Validates nullability constraints. Subclasses will expand this."""
        if value is None:
            if not self.null:
                raise ValidationError(f"Field '{self.name}' cannot be null.")
            return

    def get_sql_type(self):
        """Must be overridden by concrete field types to return SQL column syntax."""
        raise NotImplementedError("Subclasses must implement get_sql_type()")

    def to_sql(self):
        """Generates the full column constraints snippet for table creation schemas."""
        sql = f"{self.column_name} {self.get_sql_type()}"
        if self.primary_key:
            sql += " PRIMARY KEY"
        elif not self.null:
            sql += " NOT NULL"
        if self.unique:
            sql += " UNIQUE"
        return sql
    

# app/fields.py (Continued)
from datetime import datetime

class IntegerField(Field):
    def get_sql_type(self):
        # If it's a primary key, use SERIAL so Postgres auto-increments it
        return "SERIAL" if self.primary_key else "INTEGER"

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, int):
            raise ValidationError(f"Field '{self.name}' must be an integer, got {type(value).__name__}.")


class CharField(Field):
    def __init__(self, max_length: int = 255, **kwargs):
        self.max_length = max_length
        super().__init__(**kwargs)

    def get_sql_type(self):
        return f"VARCHAR({self.max_length})"

    def validate(self, value):
        super().validate(value)
        if value is not None:
            if not isinstance(value, str):
                raise ValidationError(f"Field '{self.name}' must be a string, got {type(value).__name__}.")
            if len(value) > self.max_length:
                raise ValidationError(f"Field '{self.name}' value exceeds max_length of {self.max_length}.")


class BooleanField(Field):
    def get_sql_type(self):
        return "BOOLEAN"

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, bool):
            raise ValidationError(f"Field '{self.name}' must be a boolean, got {type(value).__name__}.")


class DateTimeField(Field):
    def get_sql_type(self):
        return "TIMESTAMP"

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, datetime):
            raise ValidationError(f"Field '{self.name}' must be a Python datetime object, got {type(value).__name__}.")


class ForeignKey(Field):
    def __init__(self, to, **kwargs):
        """
        'to' argument refers to the Model class it links to.
        """
        self.to = to
        super().__init__(**kwargs)

    def __set_name__(self, owner, name):
        """Rule: For a field named 'customer', column_name becomes 'customer_id'"""
        self.name = name
        self.column_name = f"{name}_id"

    def get_sql_type(self):
        # Foreign keys match standard integer types referencing primary keys
        return "INTEGER"

    def validate(self, value):
        super().validate(value)
        # For Day 2, we validate that the ID being provided is an integer 
        # (or an object with an ID, which we will scale out further on Model days)
        if value is not None:
            if isinstance(value, int):
                return
            if hasattr(value, 'id') and isinstance(value.id, int):
                return
            raise ValidationError(f"Field '{self.name}' must provide an integer ID or a model instance.")