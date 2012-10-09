This code was started so that I can add a "regression" to attempt to deduce an actual carbohydrate reading from the data that the pump already has.  The bolus wizard has to take your word for it when you put in carbs, and it computes the insulin dose.  The problem with this is that every value put in is pretty accurate except for the carbs parameter.  So, this code has to parse through the data and:

* Find the last use of the bolus wizard
* Save those parameters for use a few hours later
* Get the next blood sugar reading from the meter
* Combine the bolus wizard parameters with the actual blood sugar reading later to compute an estimate of what the actual carbs eaten really was.

It's a simple matter of:

* Initial carb guess goes into the insulin dose.
* The insulin dose is actually given, even if the carb guess is wrong the pump can't know this
* Recompute the carb/sugar/insulin equation with the updated sugar reading a few hours later, to treat the actual sugar as the target sugar and the carbs as the variable to be solved for

It's just a simple Python script for now.  I'm maintaining this code up on github just in case there is somebody else that wants to start creating tools for the pump.  The main problems I have right now are carb counting and data duplication being created when you try to use the tools.  Some form of carb regression should probably be a feature along with the bolus wizard.  The insulin dosage is essentially a prediction made about where sugar will be in the future.  If this prediction is wrong, then one of the input variables needs revision; and as far as I can tell, it's almost always the carb input that is at fault.
