from typing import TYPE_CHECKING, List

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode


class AlwaysWrite(NextStateConditional):
    """
    hw writable, without any qualifying we/wel
    """
    comment = "HW Write"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and not field.get_property('we')
            and not field.get_property('wel')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        # TODO: make exporter promote this to an "else"?
        return "1"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)

        hwmask = field.get_property('hwmask')
        hwenable = field.get_property('hwenable')
        I = self.exp.hwif.get_input_identifier(field)
        R = f"field_storage.{field_path}"
        if hwmask is not None:
            M = self.exp.dereferencer.get_value(hwmask)
            next_val = f"{I} & ~{M} | {R} & {M}"
        elif hwenable is not None:
            E = self.exp.dereferencer.get_value(hwenable)
            next_val = f"{I} & {E} | {R} & ~{E}"
        else:
            next_val = self.exp.hwif.get_input_identifier(field)

        return [
            f"next_c = {next_val};",
            f"load_next_c = '1;",
        ]

class WEWrite(AlwaysWrite):
    comment = "HW Write - we"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('we')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        prop = field.get_property('we')
        if isinstance(prop, bool):
            identifier = self.exp.hwif.get_implied_prop_input_identifier(field, "we")
        else:
            # signal or field
            identifier = self.exp.dereferencer.get_value(prop)
        return identifier

class WELWrite(AlwaysWrite):
    comment = "HW Write - wel"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('wel')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        prop = field.get_property('wel')
        if isinstance(prop, bool):
            identifier = self.exp.hwif.get_implied_prop_input_identifier(field, "wel")
        else:
            # signal or field
            identifier = self.exp.dereferencer.get_value(prop)
        return f"!{identifier}"
