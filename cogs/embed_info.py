import nextcord, traceback, datetime
import modules.webeye as webeye
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, application_checks, tasks

class EmbedUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot: nextcord.Client = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("[\u2714] embed_info.py")
        self.embed_updater.start()   
        self.atc_updater.start() 

    @tasks.loop(seconds=60)
    async def atc_updater(self):
        xu = self.bot.get_channel(1275144994629488824)
        found = 0
        async for msg in xu.history(limit=50):
            if msg.author.id == self.bot.user.id:
                found += 1
                try:
                    atc = webeye.get_webeye("ATC")
                    atc_online = len(atc)

                    organised = {}
                    for pos in atc:
                        if "atcPosition" in pos and pos["atcPosition"] != None and pos["atcPosition"]["position"] != None:
                            if pos["atcPosition"]["airportId"] not in organised: organised[pos["atcPosition"]["airportId"]] = {}
                            identifier = ""
                            if pos["atcPosition"]["middleIdentifier"]: identifier += f'{pos["atcPosition"]["middleIdentifier"]}_'
                            identifier += pos["atcPosition"]["position"]
                            organised[pos["atcPosition"]["airportId"]][identifier] = pos["atcPosition"]["atcCallsign"]
                        elif "subcenter" in pos:
                            if "Controls" not in organised: organised["Controls"] = {}
                            identifier = pos["subcenter"]["centerId"]
                            organised["Controls"][identifier + "_CTR"] = pos["subcenter"]["atcCallsign"]
                    print(organised)
                except Exception as e: print(f"[ERROR] {traceback.format_exc()}"); break
                embed = nextcord.Embed(
                    color=nextcord.Color.from_rgb(13,44,153),
                    title=f"[XU] ATC Statistics ({atc_online} Online)",
                    description="These are the statistics for the **XU** area for the IVAO network.\nThese are updated every 60 seconds.",
                    timestamp=datetime.datetime.now()
                )
                if len(organised) == 0: embed.add_field(name="UK", value="There are no online controllers in the UK.")
                else:
                    for org in organised: # EGPH etc
                        if org == "Controls": continue
                        online_joined = ""
                        for atc_pos in organised[org]: online_joined += f"**[:green_circle:]** {org}_{atc_pos} ({organised[org][atc_pos]})\n"
                        embed.add_field(name=f"[XU] {org}", value=online_joined, inline=False)
                    if "Controls" in organised:
                        online_joined = ""
                        for atc_pos in organised["Controls"]: online_joined += f"**[:green_circle:]** {atc_pos} ({organised['Controls'][atc_pos]})\n"
                        embed.add_field(name=f"[XU] Area and Terminal", value=online_joined, inline=False)
                await msg.edit(embed=embed)
                break
        if found == 0: await xu.send(embed=nextcord.Embed(title="Initialising."))
        return

    @tasks.loop(seconds=60)
    async def embed_updater(self):
        xu = self.bot.get_channel(1275135016082604052)
        found = 0
        async for msg in xu.history(limit=50):
            if msg.author.id == self.bot.user.id:
                found += 1
                try:
                    atc = webeye.get_webeye("ATC")
                    atc_online = len(atc)

                    pilot_in = webeye.get_webeye("Pilot_Inbound")
                    pilot_in_online = len(pilot_in)

                    pilot_out = webeye.get_webeye("Pilot_Outbound")
                    pilot_out_online = len(pilot_out)

                    pilot_air = webeye.get_webeye("Pilot_In_Airspace")
                    pilot_air_online = len(pilot_air)

                    vfr = webeye.get_webeye("Pilot_VFR")
                    vfr_flights = len(vfr)

                    net = webeye.get_webeye("Network_Online")
                    net_online = net["total"]
                except Exception as e: print(f"[ERROR] {traceback.format_exc()}"); break
                embed = nextcord.Embed(
                    color=nextcord.Color.from_rgb(13,44,153),
                    title="[XU] IVAO Statistics",
                    description="These are the statistics for the **XU** area for the IVAO network.\nThese are updated every 60 seconds.",
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="UK ATC Online", value=str(atc_online))
                embed.add_field(name="Aircraft --> UK", value=str(pilot_in_online))
                embed.add_field(name="Aircraft <-- UK", value=str(pilot_out_online))
                embed.add_field(name="Aircraft in UK Airspace", value=str(pilot_air_online))
                embed.add_field(name="VFR in UK Airspace", value=str(vfr_flights))
                embed.add_field(name="Total Network Online", value=str(net_online))
                await msg.edit(embed=embed)
                break
        if found == 0: await xu.send(embed=nextcord.Embed(title="Initialising."))
        return

def setup(bot):
    bot.add_cog(EmbedUpdater(bot))
