from typing import Optional, Type

from .database import SESSION, Panel, Form, Field


class PanelModel:
    def __init__(
        self,
        guild_id,
        name,
        description,
        id=None,
        forms=None,
    ):
        self.guild_id = guild_id
        self.name = name
        self.description = description
        self.id = id
        self.forms: list[FormModel] = forms or []

    @classmethod
    def create(
        cls,
        guild_id: str,
        name: str,
        description: str = "",
    ) -> int:
        panel = Panel(guild_id=guild_id, name=name, description=description)
        try:
            SESSION.add(panel)
            SESSION.commit()
        except Exception as e:
            print(e)
            SESSION.rollback()
        return panel.id  # type: ignore

    @classmethod
    def get(cls, guild_id, panel_id) -> Optional["PanelModel"]:
        if (
            panel := SESSION.query(Panel)
            .filter_by(
                guild_id=guild_id,
                id=panel_id,
            )
            .first()
        ):
            panel.__dict__.pop("_sa_instance_state")
            panel = PanelModel(**panel.__dict__)
            panel.forms = FormModel.get_all(panel.id)
            return panel

    @classmethod
    def get_all(cls, guild_id) -> list["PanelModel"]:
        ret_list = []
        for panel in SESSION.query(Panel).filter_by(guild_id=guild_id).all():
            panel.__dict__.pop("_sa_instance_state")
            panel = PanelModel(**panel.__dict__)
            panel.forms = FormModel.get_all(panel.id)
            ret_list.append(panel)
        return ret_list

    @classmethod
    def update(cls, guild_id, panel_id, name, description):
        if panel := cls.get(guild_id, panel_id):
            panel.name = name
            panel.description = description
            SESSION.commit()
            return panel.id

    @classmethod
    def delete(cls, guild_id, panel_id):
        if panel := cls.get(guild_id, panel_id):
            SESSION.delete(panel)
            SESSION.commit()

    @classmethod
    def delete_all(cls, guild_id):
        SESSION.query(Panel).filter_by(guild_id=guild_id).delete()
        SESSION.commit()


class FormModel:
    def __init__(self, panel_id, name, description, id=None, fields=None):
        self.panel_id = panel_id
        self.name = name
        self.description = description
        self.id = id
        self.fields: list[FieldModel] = fields or []

    @classmethod
    def create(cls, panel_id, name, description=""):
        form = Form(panel_id=panel_id, name=name, description=description)
        SESSION.add(form)
        SESSION.commit()
        return form.id

    @classmethod
    def get(cls, panel_id, form_id) -> Optional["FormModel"]:
        #  Get form from database
        #  pop _sa_instance_state
        #  return FormModel
        if (
            form := SESSION.query(Form)
            .filter_by(
                panel_id=panel_id,
                id=form_id,
            )
            .first()
        ):
            form.__dict__.pop("_sa_instance_state")
            form = FormModel(**form.__dict__)
            form.fields = FieldModel.get_all(form.id)
            return form

    @classmethod
    def get_all(cls, panel_id) -> list["FormModel"]:
        #  Convert to FormModel and
        # remove _sa_instance_state from dict
        ret_list = []
        for form in SESSION.query(Form).filter_by(panel_id=panel_id).all():
            form.__dict__.pop("_sa_instance_state")
            #  Convert to FormModel
            ret_list.append(FormModel(**form.__dict__))
        return ret_list

    @classmethod
    def update(cls, panel_id, form_id, name, description):
        if form := cls.get(panel_id, form_id):
            form.name = name
            form.description = description
            SESSION.commit()
            return form.id

    @classmethod
    def delete(cls, panel_id, form_id):
        if form := cls.get(panel_id, form_id):
            SESSION.delete(form)
            SESSION.commit()

    @classmethod
    def delete_all(cls, panel_id):
        SESSION.query(Form).filter_by(panel_id=panel_id).delete()
        SESSION.commit()


class FieldModel:
    def __init__(self, form_id, name, response, id=None):
        self.form_id = form_id
        self.id = id
        self.name = name
        self.response = response

    @classmethod
    def create(cls, form_id, name, response=""):
        field = Field(form_id=form_id, name=name, response=response)
        SESSION.add(field)
        SESSION.commit()
        return field.id

    @classmethod
    def get(cls, form_id, field_id) -> Optional["FieldModel"]:
        if (
            field := SESSION.query(Field)
            .filter_by(
                form_id=form_id,
                id=field_id,
            )
            .first()
        ):
            field.__dict__.pop("_sa_instance_state")
            return FieldModel(**field.__dict__)

    @classmethod
    def get_all(cls, form_id) -> list["FieldModel"]:
        #  Convert to FieldModel and
        # remove _sa_instance_state from dict
        ret_list = []
        for field in SESSION.query(Field).filter_by(form_id=form_id).all():
            field.__dict__.pop("_sa_instance_state")
            #  Convert to FieldModel
            ret_list.append(FieldModel(**field.__dict__))
        return ret_list

    @classmethod
    def update(cls, form_id, field_id, name, response):
        if field := cls.get(form_id, field_id):
            field.name = name
            field.response = response
            SESSION.commit()
            return field.id

    @classmethod
    def delete(cls, form_id, field_id):
        if field := cls.get(form_id, field_id):
            SESSION.delete(field)
            SESSION.commit()

    @classmethod
    def delete_all(cls, form_id):
        SESSION.query(Field).filter_by(form_id=form_id).delete()
        SESSION.commit()
