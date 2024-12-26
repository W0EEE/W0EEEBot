import discord
import datetime
from discord import app_commands
        
license_class_embed_colors = {
    'A': 0x007f00,
    'C': 0xff0000,
    'E': 0xff0000,
    'T': 0xff0000,
    'X': 0xff7f00
}

def tree() -> app_commands.Group:
    group = app_commands.Group(name="fcc", description="Query the FCC ULS database for amateur-related records.")

    @group.command()
    @app_commands.describe(callsign="The callsign to look up")
    async def call(interaction: discord.Interaction, callsign: str):
        """Perform a quick lookup for basic info on a callsign."""
        await interaction.response.defer(thinking=True)
        
        callsign = callsign.strip().upper()
        
        lic = await interaction.client.uls.license_by_callsign(callsign)
        
        if lic is None:
            if interaction.client.qrz is None:
                return await interaction.followup.send(f"No results found for `{callsign}`")
            
            qrz_lic = await interaction.client.qrz.lookup_callsign(callsign)
            
            if qrz_lic is None:
                return await interaction.followup.send(f"No results found for `{callsign}`")
            
            if isinstance(qrz_lic, str):
                return await interaction.followup.send(f"Error: `{qrz_lic}`")
            
            embed = discord.Embed()
            embed.title = qrz_lic['call'].replace('0', '\u00d8')
            embed.description = '\n'.join(filter(None, [
                qrz_lic.get('name_fmt'),
                qrz_lic.get('attn'),
                qrz_lic.get('addr1'),
                qrz_lic.get('addr2'),
                qrz_lic.get('state'),
                qrz_lic.get('zip'),
                qrz_lic.get('country')
            ]))
            embed.color = 0x00007f
            
            if 'class' in qrz_lic:
                embed.add_field(name='Operator Class:', value=qrz_lic['class'], inline=False)
                
            if 'aliases' in qrz_lic:
                embed.add_field(name='AKA:', value=qrz_lic['aliases'], inline=False)

            if 'serial' in qrz_lic:
                embed.set_footer(text=f"QRZ Record #{qrz_lic['serial']}")
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="QRZ",
                url=f"https://www.qrz.com/db/{qrz_lic['call']}"
            ))
            
            return await interaction.followup.send(embed=embed, view=view)
        
        embed = discord.Embed()
        embed.title = f"{lic.callsign} ({lic.status} {lic.applicant_type})"
        embed.description = '\n'.join(filter(None, [
            lic.name,
            lic.attn_line,
            lic.po_box,
            lic.street_address,
            f"{lic.city}, {lic.state} {lic.zip}"
        ]))
        embed.color = license_class_embed_colors[lic._status] if lic._status in license_class_embed_colors else 0x7f7f7f
        
        if lic.trustee_callsign:
            embed.add_field(name='Trustee:', value=f"{lic.trustee_name}, {lic.trustee_callsign}", inline=False)
        
        if lic.operator_class:
            embed.add_field(name='Operator Class:', value=lic.operator_class, inline=False)
        
        if lic.grant_date:
            embed.add_field(name='Granted:', value=str(lic.grant_date))
            
        if lic.effective_date:
            embed.add_field(name='Effective:', value=str(lic.effective_date))
            
        if lic.expire_date:
            name = 'Expired:' if lic.expire_date < datetime.date.today() else 'Expires:'
            embed.add_field(name=name, value=str(lic.expire_date))
            
        if lic.cancel_date:
            embed.add_field(name='Canceled:', value=str(lic.cancel_date))
            
        if lic.last_action_date:
            embed.add_field(name='Last Action:', value=str(lic.last_action_date))

        embed.set_footer(text=f"FCC Record #{lic.id}")
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="QRZ",
            url=f"https://www.qrz.com/db/{lic.callsign_ascii}"
        ))
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="FCC ULS",
            url=f"https://wireless2.fcc.gov/UlsApp/UlsSearch/license.jsp?licKey={lic.id}"
        ))
        
        await interaction.followup.send(embed=embed, view=view)

    return group
