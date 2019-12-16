import drawSvg as draw
from def_parser import *
from lef_parser import *
import re
import os.path


def process(def_file, lef_file, drc_path):
    # Parse the DEF file
    # read_path = def_path
    def_parser = DefParser(def_file)
    def_parser.parse()

    # Parse the LEF file
    # path = lef_path
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    DRC_Data = []
    if os.path.exists(drc_path):
        with open(drc_path, 'r') as f:
            DRC_Data = f.read().split()
            print(DRC_Data)
        f.close()

    violations_point1 = []
    violations_point2 = []
    violations_types = []
    violations_sources = []
    violations_layers = []

    for i in range(0, len(DRC_Data)):
        if DRC_Data[i] == "bbox":
            violations_point1.append(DRC_Data[i + 2] + DRC_Data[i + 3])
            violations_point2.append(DRC_Data[i + 5] + DRC_Data[i + 6])
        if DRC_Data[i] == "type:":
            violations_types.append(DRC_Data[i + 1])
        if DRC_Data[i] == "srcs:":
            pointer = i + 1
            src = ""
            while DRC_Data[pointer] != "bbox":
                src = src + " " + DRC_Data[pointer]
                pointer = pointer + 1
            violations_sources.append(src)
        if DRC_Data[i] == "Layer":
            violations_layers.append(DRC_Data[i + 1])
    print("Start parsing")
    print(violations_point1)
    print(violations_point2)
    print(violations_types)
    print(violations_sources)
    print(violations_layers)

    # Parsing the LEF outputs the data into LEF_Parsed.txt which is saved in the variable named file
    # file.close()
    file = open("LEF_Parsed.txt", "r")
    LEF = file.read().split()  # Now LEF list contains all the LEF data

    # Get the Die dimensions from the Die area
    Die_Area = def_parser.diearea
    Die_Dim = re.split('[(), ]', str(Die_Area))
    Global_X = float(Die_Dim[1])
    Global_Y = float(Die_Dim[3])
    Die_Width = float(float(Die_Dim[7]) - float(Die_Dim[1]))
    Die_Height = float(float(Die_Dim[9]) - float(Die_Dim[3]))

    # Declare d which will be our layout svg
    # The dimensions will be the Die_width+2000 and the Die_Height+2000
    # The +2000 is to give spacing from all directions and the die area will be centralized in the picture
    d = draw.Drawing(Die_Width + 2000, Die_Height + 2000, origin=(0, -(Die_Height + 2000)))

    # This rectangle will be the background of the Die Area
    d.append(draw.Rectangle(1000, (-(Die_Height + 1000)), Die_Width, Die_Height, fill='yellow', fill_opacity=0.2,
                            stroke_width=10, stroke='black'))

    cell_names = []
    pin_names = []
    net_names = []
    cell_types = []
    for key, val in def_parser.components.comp_dict.items():  # Loop to draw the components
        x = str(val).split()
        cell_names.append(x[1])

        macro = str(x[3])  # Macro now holds the name of the Macro to be drawn in the DEF File
        add = True
        for cell_type in cell_types:
            if x[3] == cell_type:
                add = False
        if add:
            cell_types.append(x[3])

        y = str((x[5] + x[6]))
        z = y.split(',')
        height_Bracket_Array = z[1].split(']')
        y_pos = float(height_Bracket_Array[0])  # y_pos is where that component wil be placed in the y direction
        width_Bracket_Array = z[0].split('[')
        x_pos = float(width_Bracket_Array[1])  # x_pos is where that component wil be placed in the x direction
        flip = x[7]  # Flip contains the orientation of the component N,FN,S,FS

        # Now that we got all the necessary info about the component to be drawn from the DEF file
        # We go to search that component from the LEF file to start drawing

        start_index = LEF.index(macro)  # Start index shows the beginning of the macro declaration in the LEF file
        end_index = LEF.index("END", start_index)  # End index shows the end of the macro declaration in the LEF file
        pin_name = " "
        layer_used = " "
        color = " "
        opacity = 0.0
        cell_height = 0.0
        cell_width = 0.0
        # Now we loop on the macro description from the LEF file to draw that component
        g = draw.Group(fill="black", Class="cell", id=x[1])

        for i in range(start_index, end_index):
            if LEF[i] == "PIN":  # Setting the Pin name
                pin_name = LEF[i + 1]
            if LEF[i] == "Layer":  # Setting the layer used
                layer_used = LEF[i + 1]
            if LEF[i] == "Size":  # setting the cell's width and height
                cell_width = float(LEF[i + 1]) * 100
                cell_height = float(LEF[i + 2]) * 100
                d.append(draw.Rectangle(x_pos + 1000 - Global_X, -(Die_Height + 1000 - (y_pos - Global_Y)), cell_width,
                                        cell_height,
                                        fill='transparent', stroke_width=1, stroke='black', id=x[3]))
                d.append(draw.Rectangle(x_pos + 1000 - Global_X, -(Die_Height + 1000 - (y_pos - Global_Y)), cell_width,
                                        cell_height,
                                        fill='transparent', stroke_width=1, stroke='black', id="z" + x[1]))

            if pin_name == "OBS":  # Setting the opacity based on whether it is an OBS or not
                opacity = 0.7
            else:
                opacity = 0.3

            # Setting the color based on which layer is used
            if layer_used == "metal1":  # Salmon color
                color = '#ff8c69'
            elif layer_used == "metal2":  # Pink color
                color = '#ffc0cb'
            elif layer_used == "metal3":  # Aqua color
                color = '#00ffff'
            elif layer_used == "metal4":  # Brown color
                color = '#964b00'
            elif layer_used == "via1":  # Red color
                color = '#de1738'
            elif layer_used == "via2":  # Purple color
                color = '#610aa2'
            elif layer_used == 'via3':  # Baby Blue color
                color = '#05f0ec'

            if LEF[i] == "RECT":  # Drawing all the component's rectangles
                x0 = float(LEF[i + 1]) * 100
                y0 = float(LEF[i + 2]) * 100
                x1 = float(LEF[i + 3]) * 100
                y1 = float(LEF[i + 4]) * 100
                # In case of Flipped N
                if flip == "N":
                    if pin_name == "OBS":
                        g.append(
                            draw.Rectangle((x_pos + 1000 - Global_X + x0),
                                           -(Die_Height + 1000 - (y0 + y_pos - Global_Y)), (x1 - x0), (y1 - y0),
                                           fill=color, fill_opacity=opacity, stroke_width=1, stroke='black', id=pin_name))
                    else:
                        g.append(
                            draw.Rectangle((x_pos + 1000 - Global_X + x0),
                                           -(Die_Height + 1000 - (y0 + y_pos - Global_Y)), (x1 - x0), (y1 - y0),
                                           fill=color, fill_opacity=opacity, stroke_width=1, stroke='black',
                                           id=layer_used))
                        g.append(draw.Text(pin_name, 30,
                                           ((x_pos + 1000 - Global_X + x0) + (x_pos + 1000 - Global_X + x1)) / 2,
                                           -(Die_Height + 1000 - (
                                                   ((y0 + y_pos - Global_Y) + (y1 + y_pos - Global_Y)) / 2)),
                                           center='origin', id=layer_used))


                # In case of Flipped FN
                elif flip == "FN":
                    if pin_name == "OBS":
                        g.append(draw.Rectangle((x_pos + 1000 - Global_X - x1 + cell_width),
                                            -(Die_Height + 1000 - (y0 + y_pos - Global_Y)),
                                            (x1 - x0), (y1 - y0), fill=color, fill_opacity=opacity, stroke_width=1,
                                            stroke='black', id=pin_name))
                    else:
                        g.append(draw.Rectangle((x_pos + 1000 - Global_X - x1 + cell_width),
                                                -(Die_Height + 1000 - (y0 + y_pos - Global_Y)),
                                                (x1 - x0), (y1 - y0), fill=color, fill_opacity=opacity, stroke_width=1,
                                                stroke='black', id=layer_used))
                        g.append(draw.Text(pin_name, 30,
                                           ((x_pos + 1000 - Global_X + cell_width - x1) + (
                                                   x_pos + 1000 - Global_X + cell_width - x0)) / 2,
                                           -(Die_Height + 1000 - (
                                                   ((y0 + y_pos - Global_Y) + (y1 + y_pos - Global_Y)) / 2)),
                                           center='origin', id=layer_used))

                # In case of Flipped FS
                elif flip == "FS":
                    if pin_name == "OBS":
                        g.append(draw.Rectangle(1000 + (x_pos - Global_X + x0),
                                            -(Die_Height + 1000 - (cell_height - y1 + y_pos - Global_Y)),
                                            (x1 - x0), (y1 - y0), fill=color, fill_opacity=opacity,
                                            stroke_width=1, stroke='black', id=pin_name))
                    else:
                        g.append(draw.Rectangle(1000 + (x_pos - Global_X + x0),
                                                -(Die_Height + 1000 - (cell_height - y1 + y_pos - Global_Y)),
                                                (x1 - x0), (y1 - y0), fill=color, fill_opacity=opacity,
                                                stroke_width=1, stroke='black', id=layer_used))
                        g.append(draw.Text(pin_name, 30,
                                           ((x_pos + 1000 - Global_X + x0) + (x_pos + 1000 - Global_X + x1)) / 2,
                                           -(Die_Height + 1000 - (((cell_height - y1 + y_pos - Global_Y)
                                                                   + (cell_height - y0 + y_pos - Global_Y)) / 2)),
                                           center='origin', id=layer_used))

                # In case of Flipped S
                elif flip == "S":
                    if pin_name == "OBS":
                        g.append(draw.Rectangle(1000 + (x_pos - Global_X - x1 + cell_width),
                                            -(Die_Height + 1000 - (cell_height - y1 + y_pos - Global_Y)), (x1 - x0),
                                            (y1 - y0), fill=color, fill_opacity=opacity, stroke_width=1,
                                            stroke='black', id=pin_name))
                    else:
                        g.append(draw.Rectangle(1000 + (x_pos - Global_X - x1 + cell_width),
                                                -(Die_Height + 1000 - (cell_height - y1 + y_pos - Global_Y)), (x1 - x0),
                                                (y1 - y0), fill=color, fill_opacity=opacity, stroke_width=1,
                                                stroke='black', id=layer_used))
                        g.append(draw.Text(pin_name, 30, ((x_pos + 1000 - Global_X + cell_width - x1) +
                                                          (x_pos + 1000 - Global_X + cell_width - x0)) / 2,
                                           -(Die_Height + 1000 - (((cell_height - y1 + y_pos - Global_Y)
                                                                   + (cell_height - y0 + y_pos - Global_Y)) / 2)),
                                           center='origin', id=layer_used))
        d.append(g)

    for key, val in def_parser.nets.net_dict.items():  # Loop to draw the VIAs
        x = str(val).split()
        start_route = x.index("Routed:")  # Start the loop when the word "Routed:" is found
        for i in range(start_route + 1, len(x)):
            # If a VIA is found, the 2 previous coordinates will be the VIA position
            if x[i] == "M2_M1" or x[i] == "M3_M2" or x[i] == "M4_M3":
                coordinate = str(x[i - 2]) + str(x[i - 1])
                z = coordinate.split(',')
                x_pos = z[0].split('[')
                y_pos = z[1].split(']')

                layer_used = " "
                color = " "
                start_index = LEF.index(x[i])  # Start index shows the beginning of the VIA declaration in the LEF file
                end_index = LEF.index("END",
                                      start_index)  # End index shows the end of the VIA declaration in the LEF file
                # Loop on the VIA description to draw the VIA rectangles
                for j in range(start_index, end_index):
                    if LEF[j] == "Layer":  # Setting the layer used
                        layer_used = LEF[j + 1]
                    # print(layer_used)

                    if layer_used == "metal1":  # Salmon color
                        color = '#ff8c69'
                    elif layer_used == "metal2":  # Pink color
                        color = '#ffc0cb'
                    elif layer_used == "metal3":  # Aqua color
                        color = '#00ffff'
                    elif layer_used == "metal4":  # Brown color
                        color = '#964b00'
                    elif layer_used == "via1":  # Red color
                        color = '#de1738'
                    elif layer_used == "via2":  # Purple color
                        color = '#610aa2'
                    elif layer_used == 'via3':  # Baby Blue color
                        color = '#05f0ec'

                    if LEF[j] == "RECT":  # Drawing all the component's rectangles
                        x0 = float(LEF[j + 1]) * 100
                        y0 = float(LEF[j + 2]) * 100
                        x1 = float(LEF[j + 3]) * 100
                        y1 = float(LEF[j + 4]) * 100

                        d.append(draw.Rectangle(1000 + (float(x_pos[1]) - Global_X + x0),
                                                -(Die_Height + 1000 - (y0 + float(y_pos[0])
                                                                       - Global_Y)), (x1 - x0),
                                                (y1 - y0),
                                                fill=color, fill_opacity=0.3, stroke_width=1, stroke='black',
                                                id=layer_used))

    for key, val in def_parser.nets.net_dict.items():  # Loop to Draw the routed paths
        x = str(val).split()
        net_names.append(x[1])
        g = draw.Group(fill="black", Class="cell", id=x[1])
        start_route = x.index("Routed:")
        for i in range(start_route + 1, len(x)):
            # Whenever found a metal declaration, a new route is declared and we need to get the number of coordinates preceeding
            if x[i] == "metal1" or x[i] == "metal2" or x[i] == "metal3" or x[i] == "metal4":
                color = ""
                width = 0
                layer_used = x[i]
                # Setting the color based on which layer is used
                if layer_used == "metal1":  # Salmon color
                    width = 60  # Path width = 60 in case of metal1
                    color = '#ff8c69'
                elif layer_used == "metal2":  # Pink color
                    width = 60  # Path width = 60 in case of metal2
                    color = '#ffc0cb'
                elif layer_used == "metal3":  # Aqua color
                    width = 60  # Path width = 60 in case of metal3
                    color = '#00ffff'
                elif layer_used == "metal4":  # Brown color
                    width = 120  # Path width = 120 in case of metal4
                    color = '#964b00'
                elif layer_used == "via1":  # Red color
                    color = '#de1738'
                elif layer_used == "via2":  # Purple color
                    color = '#610aa2'
                elif layer_used == 'via3':  # Baby Blue color
                    color = '#05f0ec'
                coordinate_count = 0  # Has the number of coordinates per each metal declaration
                factor = 1
                coordinates = [""] * 15  # An array of coordinates to contain all the pairs found
                while True:
                    # There must be at least one coordinate after each metal declaration
                    coordinates[coordinate_count] = str(x[i + factor] + x[i + factor + 1])
                    coordinate_count = coordinate_count + 1
                    factor = factor + 2
                    # If the one of the following condition is true, then the path declaration is over
                    if x[i + factor] == "M2_M1" or x[i + factor] == "M3_M2" or x[i + factor] == "M4_M3" or \
                            x[i + factor] == "metal1" or x[i + factor] == "metal2" or \
                            x[i + factor] == "metal3" or x[i + factor] == "metal4" or len(x) == i + factor + 1:
                        break
                if coordinate_count > 1:  # Start drawing the path if we have more than one coordinate
                    factor2 = 0
                    while True:
                        first_co = coordinates[factor2].split('[')
                        x0 = float(first_co[1].split(',')[0])  # x0 will always contain the starting x position
                        y0 = float(
                            first_co[1].split(',')[1].split(']')[0])  # y0 will always contain the starting y position
                        second_co = coordinates[factor2 + 1].split('[')
                        x1 = float(second_co[1].split(',')[0])  # x1 will always contain the end x position
                        y1 = float(
                            second_co[1].split(',')[1].split(']')[0])  # y1 will always contain the end y position
                        p = draw.Path(fill_opacity=0, stroke_width=width, stroke=color, stroke_opacity=0.5, id=layer_used)
                        p.M(1000 + x0 - Global_X, -(Die_Height + 1000 - (y0 - Global_Y)))  # Start path at point (x0,y0)
                        p.l(x1 - x0, y1 - y0)  # Draw a line from (x0,y0) to (x1,y1)
                        g.append(p)  # Add the path to our drawing
                        coordinate_count = coordinate_count - 1
                        factor2 = factor2 + 1
                        if coordinate_count == 1:
                            break
        d.append(g)

    for key, val in def_parser.pins.pin_dict.items():  # Loop to draw the Pins
        pin_name = key  # Contain the name of the pin to be printed
        pin_names.append(key)
        pos = str(val.placed)
        x = float(pos.split()[0].split(',')[0].split('[')[1])  # X position of the pin
        y = float(pos.split()[1].split(']')[0])  # Y position of the pin

        LAYER_SIZE = str(val.layer)
        layer_used = LAYER_SIZE.split()[0]
        width = float(LAYER_SIZE.split()[3].split(',')[0].split('[')[1]) - float(
            LAYER_SIZE.split()[1].split(',')[0].split('[')[1])  # Width of the pin
        height = float(LAYER_SIZE.split()[4].split(']')[0]) - float(
            LAYER_SIZE.split()[2].split(']')[0])  # Height of the pin
        if layer_used == "metal1":  # Salmon color
            color = '#ff8c69'
        elif layer_used == "metal2":  # Pink color
            color = '#ffc0cb'
        elif layer_used == "metal3":  # Aqua color
            color = '#00ffff'
        elif layer_used == "metal4":  # Brown color
            color = '#964b00'
        elif layer_used == "via1":  # Red color
            color = '#de1738'
        elif layer_used == "via2":  # Purple color
            color = '#610aa2'
        elif layer_used == 'via3':  # Baby Blue color
            color = '#05f0ec'

        d.append(draw.Rectangle((1000 + x - Global_X), -(Die_Height + 1000 - (y - Global_Y)), width, height, fill=color,
                                fill_opacity=0.5,
                                stroke_width=1, stroke='black', id=layer_used))
        d.append(draw.Text(pin_name, 30, 1000 + x - Global_X, -(Die_Height + 1000 - (y - Global_Y)), center='origin'))

    d.saveSvg('./static/FinalLayout14.svg')

    d  # Display as SVG
    print("The layout is now saved in Layout.svg")
    return cell_types, cell_names, pin_names, net_names
