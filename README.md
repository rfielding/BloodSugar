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
Example:

    12/06/10 10:08:05 5:BG Reading (mg/dL): 85
    12/06/10 10:10:25 23:BWZ Carb Input (grams): 40
    12/06/10 10:10:25 24:BWZ BG Input (mg/dL): 85
    12/06/10 14:14:21 5:BG Reading (mg/dL): 154
    *12/06/10 10:10:25 -1:actualfood: 48.8*
    *12/06/10 10:10:25 -1:actualerr: 18%*
    12/06/10 14:14:34 23:BWZ Carb Input (grams): 30
    12/06/10 14:14:34 24:BWZ BG Input (mg/dL): 154
    12/06/10 17:16:37 5:BG Reading (mg/dL): 160
    *12/06/10 14:14:34 -1:actualfood: 40.4*
    *12/06/10 14:14:34 -1:actualerr: 25%*
    12/06/10 19:26:39 5:BG Reading (mg/dL): 143
    12/06/10 19:27:33 23:BWZ Carb Input (grams): 60
    12/06/10 19:27:33 24:BWZ BG Input (mg/dL): 143
    12/06/10 19:52:10 23:BWZ Carb Input (grams): 60
    12/06/10 19:52:10 24:BWZ BG Input (mg/dL): 154
    12/06/10 22:48:37 5:BG Reading (mg/dL): 95
    *12/06/10 19:52:10 -1:actualfood: 53.0666666667*
    *12/06/10 19:52:10 -1:actualerr: -13%*
    12/06/10 23:48:27 5:BG Reading (mg/dL): 107
    12/07/10 01:40:45 5:BG Reading (mg/dL): 86
    12/07/10 09:31:05 5:BG Reading (mg/dL): 68
    12/07/10 10:21:26 23:BWZ Carb Input (grams): 65
    12/07/10 10:21:26 24:BWZ BG Input (mg/dL): 70
    12/07/10 13:10:01 5:BG Reading (mg/dL): 115
    *12/07/10 10:21:26 -1:actualfood: 63.2*
    *12/07/10 10:21:26 -1:actualerr: -2%*


The estimates are based on trivial formulas that you should be able to do in your head after a while.  The first is how much to inject based on where your sugar is, and how many carbohydrates you think you are eating:

    //Insulin = Food/CarbToInsulinRatio + (Reading-Target)/SugarToInsulinRatio
    I = F/CIR + (R-T)/SIR

But if we take a reading later and we did not land at T, but instead landed at another value L, then we can just replace variable F with a variable G.  G is our revised estimate of the grams of carb that we ate, while L is the landing (rather than Target) sugar:

    I = G/CIR + (R-L)/SIR
    I + (L-R)/SIR = G/CIR
    CIR*I + CIR/SIR*(L-R) = G

So, that's a revised estimate of carbs.  It requires that we get data from the bolus wizard, and use a blood sugar reading a few hours later and combine to figure out G.  We can take the standard data and enhance it with derived variables like this.  Perhaps the output of the Python script should be generating something suitable for gnuplot or Google Charts.  This is something I am still working on.


