from os import remove, getcwd
from os.path import join as path_join
import traceback
from uuid import uuid4

from discord import (
    ButtonStyle,
    Embed,
    File,
    Interaction,
    Member,
    Message,
    TextChannel,
    TextStyle,
    utils,
)
from discord.ui import Button, Modal, TextInput, View, button
from tickets.models import PanelModel, FormModel, FieldModel

from tickets.history_html import HTML, message


def export_html(file_name: str, messages: list[Message]) -> str:
    if not file_name.endswith(".html"):
        file_name = f"{file_name}.html"
    file_name = path_join(getcwd(), file_name)
    string = [
        message.format(
            m.created_at.strftime("%H:%M"),
            m.author,
            m.clean_content,
        )
        for m in messages
    ]
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(HTML.format("\n".join(string)))
    return file_name


class PanelButton(Button):
    def __init__(self, form: FormModel, **kwargs):
        super().__init__(
            **kwargs,
        )
        self.form = form

    async def callback(self, interaction: Interaction):
        fields = FieldModel.get_all(self.form.id)
        inputs = [field.name for field in fields]
        await interaction.response.send_modal(Form(inputs))


class PanelView(View):
    def __init__(self, panel: PanelModel | None = None):
        super().__init__()
        self.value = None
        if panel is None:
            return
        forms = FormModel.get_all(panel.id)
        for form in forms:
            button = PanelButton(
                label=form.name,
                style=ButtonStyle.green,
                custom_id=str(form.id),
                form=form,
            )
            self.add_item(button)


class TicketView(View):
    def __init__(self):
        super().__init__()
        self.value = None

    @button(
        label="Close Ticket",
        style=ButtonStyle.green,
        custom_id=str(uuid4()),
    )
    async def confirm(self, interaction: Interaction, button: Button):
        mention = interaction.user.mention
        self.value = f"{mention} Closed a ticket"
        #  Export chat history to a file
        if not isinstance((channel := interaction.channel), TextChannel):
            return
        messages = [
            message
            async for message in channel.history(
                limit=None,
                oldest_first=True,
            )
        ]
        file_name = "ticket"
        file_name = export_html(file_name, messages)
        if guild := interaction.guild:
            channel = utils.get(guild.channels, name="ticket-info")
            if channel is None:
                channel = await guild.create_text_channel("ticket-info")
            if not isinstance(channel, TextChannel):
                return
            await channel.send(file=File(file_name))
            await interaction.response.send_message(self.value)

            remove(file_name)
        #  Close the channel
        if isinstance(channel := interaction.channel, TextChannel):
            await channel.delete(reason="Ticket closed")


#  A view to ask user his name
class Form(Modal, title="Ticket"):
    def __init__(self, inputs: list[str]):
        super().__init__()
        for input in inputs:
            self.add_item(TextInput(label=input, required=True))

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(
            "Thanks for your response!",
            ephemeral=True,
        )
        if guild := interaction.guild:
            channel_name = f"ticket-{uuid4().int}"
            my_channel = await guild.create_text_channel(channel_name)
            #  Add role to user and channel
            if user := interaction.user:
                if isinstance(user, Member):
                    await my_channel.set_permissions(
                        user,
                        read_messages=True,
                        send_messages=True,
                    )
                    await my_channel.set_permissions(
                        guild.default_role,
                        read_messages=False,
                        send_messages=False,
                    )
                    my_embed = Embed(
                        title="Ticket",
                        description="New support ticket",
                    )
                    for inp in self.children:
                        if isinstance(inp, TextInput):
                            my_embed.add_field(
                                name=inp.label,
                                value=inp.value,
                                inline=False,
                            )
                    my_embed.set_footer(text="Ticket created")
                    my_embed.set_author(
                        name=user.display_name,
                        icon_url=user.avatar.url
                        if user.avatar
                        else user.default_avatar.url,
                    )
                    await my_channel.send(
                        content=user.mention,
                        embed=my_embed,
                        view=TicketView(),
                    )

    async def on_error(
        self,
        interaction: Interaction,
        error: Exception,
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.",
            ephemeral=True,
        )

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)
