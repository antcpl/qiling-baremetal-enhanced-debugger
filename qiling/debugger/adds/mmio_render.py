
from ..const import color
import os


"""

    Context Render for rendering UI

"""

COLORS = (color.DARKCYAN, color.BLUE, color.RED, color.YELLOW, color.GREEN, color.PURPLE, color.CYAN, color.WHITE)

class Render:
    """
    base class for rendering related functions
    """

    def divider_printer(field_name, ruler="─"):
        """
        decorator function for printing divider and field name
        """

        def decorator(context_dumper):
            def wrapper(*args, **kwargs):
                try:
                    width, _ = os.get_terminal_size()
                except OSError:
                    width = 130

                bar = (width - len(field_name)) // 2 - 1
                print(ruler * bar, field_name, ruler * bar)
                context_dumper(*args, **kwargs)
                if "MMIO" in field_name:
                    print(ruler * width)

            return wrapper
        return decorator

    def __init__(self):
        self.regs_a_row = 4
        self.stack_num = 10
        self.disasm_num = 0x10
        self.color = color

    def bit_counter(self,value)->list:
        return [i for i in range(32) if (value >> i) & 1]

    def render_mmio_access(self)->None: 
        """
        Printer for rendering mmio access 
        """

        access_type = {17: "UC_MEM_WRITE", 16: "UC_MEM_READ"}
        for d in self.track_list : 
            basic = "{0} \t: 0x{1:08x} {2} —▸ {3} \t".format(access_type[d["access"]],d["addr"],d["size"],d["name"]) 
            curr_value = "0x{0:08x}\t".format(int.from_bytes(d["curr_value"],"little")) if d["curr_value"] else ""
            pile = "pile : {0}\t".format(d["pile"][:4]) if d.get("pile") else ""
            written_value = " written value : 0x{0:08x}  0b{1:032b}  {2}".format(d["value"], d["value"], self.bit_counter(d["value"])) if d["access"]==17 else ""
            print(f"{basic} {curr_value} {color.RED}{pile}{color.END} {written_value}")


    def render_subroutines(self)->None: 
        space = 0
        for i in self.subroutine_tracking_list[-4:]:
            sub = " " * space + "—▸ {0}".format(i)
            name=""
            if self.subroutine_provided_dic is not None: 
                name = "  ===> {0}".format(self.subroutine_provided_dic[i]) if i in self.subroutine_provided_dic else ""
            print(f"{sub} {name}")
            space+=1