#Task 1
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from password import sql_password
#Task 2
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

#Task 1
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{sql_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
#Task 2
ma = Marshmallow(app)

#Task 2
class MemberSchema(ma.Schema):
    id = fields.Integer(required=True, validate=validate.Range(min=1))
    name = fields.String(require=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True, validate=validate.Range(min=0))
    
    class Meta:
        fields = ("id", "name", "age")

#Task 3
class WorkoutSessionSchema(ma.Schema):
    session_id = fields.Integer(required=True, validate=validate.Range(min=0))
    member_id = fields.Integer(required=True, validate=validate.Range(min=0))
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True, validate=validate.Length(min=1))
    activity = fields.String(required=True, validate=validate.Length(min=1))

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

#Task 2
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

#Task 3
workoutsession_schema = WorkoutSessionSchema()
workoutsessions_schema = WorkoutSessionSchema(many=True)

#Task 1
class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(255), nullable=False)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    workoutsessions = db.relationship('WorkoutSession', backref='member')



#Task 2
#Default route
@app.route('/')
def home():
    return 'Welcome to the Fitness Center Management System!'

#Get all members
@app.route("/members", methods=["GET"])
def get_members():
    #fetching the members and returning JSON response
    members = Member.query.all()
    return members_schema.jsonify(members)
 
#Add new member    
@app.route('/members', methods=['POST'])
def add_member():
    try:
        #Validate and deserialize input using Marshmallow
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    #Prepare input data for adding to Database
    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    
    #Add new member to Database and commit
    db.session.add(new_member)
    db.session.commit()
    
    #Success JSON Message return
    return jsonify({"message": "New member added successfully"}),201

#Update a member
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    #verify member
    member = Member.query.get_or_404(id)
    try:
        #Validate and deserialize input using Marshmallow
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.id = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

#Delete a member
@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    #Verify member
    member = Member.query.get_or_404(id)
    #Delete member
    db.session.delete(member)
    db.session.commit()
    #success message
    return jsonify({"message": "Customer removed successfully"}), 200

#Task 3
#Add a Workout session
@app.route('/workoutsessions', methods=['POST'])
def add_workout_session():
    try:
        #Validate and deserialize input using Marshmallow
        workoutsession_data = workoutsession_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    #setup data for database
    new_session = WorkoutSession(session_id=workoutsession_data['session_id'], member_id=workoutsession_data['member_id'], session_date=workoutsession_data['session_date'], session_time=workoutsession_data['session_time'], activity=workoutsession_data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "Workout Session was added successfully"}), 201

@app.route('/workoutsessions', methods=['GET'])
def get_workout_session():
    workoutsessions = WorkoutSession.query.all()
    return workoutsessions_schema.jsonify(workoutsessions)

@app.route('/workoutsessions/<int:session_id>', methods=['PUT'])
def update_workout_session(session_id):
    #Verify workout session
    workoutsession = WorkoutSession.query.get_or_404(session_id)
    try:
        #Validate and deserialize input using Marshmallow
        session_data = workoutsession_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    

    #update database with input
    workoutsession.session_id = session_data['session_id']
    workoutsession.member_id = session_data['member_id']
    workoutsession.session_date = session_data['session_date']
    workoutsession.session_time = session_data['session_time']
    workoutsession.activity = session_data['activity']
    db.session.commit()
    #success message
    return jsonify({"message": "Workout Session updated successfully"}),200

@app.route('/workoutsessions/<int:session_id>', methods=['DELETE'])
def delete_workout_session(session_id):
    #Verify workout session
    workoutsession = WorkoutSession.query.get_or_404(session_id)
    #Delete the selected workout session
    db.session.delete(workoutsession)
    db.session.commit()
    #success message
    return jsonify({"message": "Product deleted successfully"}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)