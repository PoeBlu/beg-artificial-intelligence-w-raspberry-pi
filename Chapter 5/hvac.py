import numpy as np
import skfuzzy as fuzz

# Generate universe variables
#   * room and target temperature range is 50 to 90
#   * same for the output control variable
x_room_temp    = np.arange(50, 91, 1)
x_target_temp  = np.arange(50, 91, 1)
x_control_temp = np.arange(50, 91, 1)

# Generate fuzzy membership functions
room_temp_lo     = fuzz.trimf(x_room_temp,   [50, 50, 70])
room_temp_md     = fuzz.trimf(x_room_temp,   [50, 70, 90])
room_temp_hi     = fuzz.trimf(x_room_temp,   [70, 90, 90])
target_temp_lo   = fuzz.trimf(x_target_temp, [50, 50, 70])
target_temp_md   = fuzz.trimf(x_target_temp, [50, 70, 90])
target_temp_hi   = fuzz.trimf(x_target_temp, [50, 90, 90])
control_temp_lo  = fuzz.trimf(x_control_temp,[50, 50, 70])
control_temp_md  = fuzz.trimf(x_control_temp,[50, 70, 90]) 
control_temp_hi  = fuzz.trimf(x_control_temp,[70, 90, 90])


# Get user inputs
room_temp = raw_input('Enter room temperature 50 to 90: ')
target_temp = raw_input('Enter target temperature 50 to 90: ')

# Calculate degrees of membership
room_temp_level_lo = fuzz.interp_membership(x_room_temp, room_temp_lo, float(room_temp))
room_temp_level_md = fuzz.interp_membership(x_room_temp, room_temp_md, float(room_temp))
room_temp_level_hi = fuzz.interp_membership(x_room_temp, room_temp_hi, float(room_temp))

target_temp_level_lo = fuzz.interp_membership(x_target_temp, target_temp_lo, float(target_temp))
target_temp_level_md = fuzz.interp_membership(x_target_temp, target_temp_md, float(target_temp))
target_temp_level_hi = fuzz.interp_membership(x_target_temp, target_temp_hi, float(target_temp))

# Apply all six rules
# rule 1:  if room_temp is cold and target temp is comfortable then command is heat
active_rule1 = np.fmin(room_temp_level_lo, target_temp_level_md)
control_activation_1 = np.fmin(active_rule1, control_temp_hi)  

# rule 2: if room_temp is cold and target temp is hot then command is heat
active_rule2 = np.fmin(room_temp_level_lo, target_temp_level_hi)
control_activation_2 = np.fmin(active_rule2, control_temp_hi)

# rule 3: if room_temp is comfortable and target temp is cold then command is cool
active_rule3 = np.fmin(room_temp_level_md, target_temp_level_lo)
control_activation_3 = np.fmin(active_rule3, control_temp_lo)

# rule 4: if room_temp is comfortable and target temp is heat then command is heat
active_rule4 = np.fmin(room_temp_level_md, target_temp_level_hi)
control_activation_4 = np.fmin(active_rule4, control_temp_hi)

# rule 5: if room_temp is hot and target temp is cold then command is cool
active_rule5 = np.fmin(room_temp_level_hi, target_temp_level_lo)
control_activation_5 = np.fmin(active_rule5, control_temp_lo)

# rule 6: if room_temp is hot and target temp is comfortable then command is cool
active_rule6 = np.fmin(room_temp_level_hi, target_temp_level_md)
control_activation_6 = np.fmin(active_rule6, control_temp_lo)

# Aggregate all six output membership functions together
# Combine outputs to ease the complexity as fmax() only as two args
c1 = np.fmax(control_activation1, control_activation2)
c2 = np.fmax(control_activation3, control_activation4)
c3 = np.fmax(control_activation5, control_activation6)
c4 = np.fmax(c2,c3)
aggregated = np.fmax(c1, c4)

# Calculate defuzzified result using the method of centroids
control_value = fuzz.defuzz(x_control_temp, aggregated, 'centroid')

#  Display the crisp output value
print control_value
