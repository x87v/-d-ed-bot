import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} olarak giriş yapıldı!")
    print("Bot hazır, komutları bekliyor...")

# ==========================================
# HATA YAKALAYICI (Yetki Kontrolü)
# ==========================================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu sadece **Yöneticiler (Adminler)** kullanabilir!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik bilgi girdin! Komutun nasıl kullanıldığını görmek için `!yardım` yazabilirsin.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Geçersiz bir ID girdin! Lütfen sadece sayılardan oluşan bir ID gir.")
    else:
        print(f"Bir hata oluştu: {error}")

# ==========================================
# !yardım KOMUTU
# ==========================================
@bot.command(name="yardım")
async def yardim(ctx):
    embed = discord.Embed(
        title="🤖 Bot Komut Menüsü",
        description="Aşağıda botun kullanabileceğin tüm komutları listelenmiştir:",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="🗑️ `!sil (kanal_id) (kullanıcı_id)`",
        value="Belirtilen kanalda, belirtilen kullanıcının son 100 mesajını siler.\n*(Sadece Adminler)*",
        inline=False
    )
    embed.add_field(
        name="ℹ️ `!bilgi (kullanıcı_id)`",
        value="Belirtilen kullanıcının hesap açılış ve sunucuya katılma tarihi gibi bilgilerini gösterir.\n*(Sadece Adminler)*",
        inline=False
    )
    embed.set_footer(text="7kgu Bot Sistemi", icon_url=bot.user.display_avatar.url)
    
    await ctx.send(embed=embed)

# ==========================================
# !sil KOMUTU (Sadece Adminler)
# ==========================================
@bot.command(name="sil")
@commands.has_permissions(administrator=True) 
async def mesaj_sil(ctx, channel_id: int, user_id: int):
    channel = bot.get_channel(channel_id)
    
    if not channel:
        await ctx.send("❌ Belirttiğin ID'ye sahip bir kanal bulunamadı!")
        return

    try:
        def is_user_message(message):
            return message.author.id == user_id

        deleted = await channel.purge(limit=100, check=is_user_message)
        
        await ctx.send(f"✅ {channel.mention} kanalında <@{user_id}> kullanıcısına ait **{len(deleted)}** mesaj silindi.", delete_after=5)
    
    except discord.Forbidden:
        await ctx.send("❌ Bu kanaldaki mesajları silmek için yeterli yetkim yok! Lütfen botun 'Mesajları Yönet' yetkisi olduğundan emin ol.")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {e}")

# ==========================================
# !bilgi KOMUTU (Sadece Adminler)
# ==========================================
@bot.command(name="bilgi")
@commands.has_permissions(administrator=True) 
async def kullanici_bilgi(ctx, user_id: int):
    try:
        member = ctx.guild.get_member(user_id)
        if not member:
            user = await bot.fetch_user(user_id)
        else:
            user = member

        hesap_tarihi = user.created_at.strftime("%d %B %Y, %H:%M")

        embed = discord.Embed(title=f"👤 Kullanıcı Bilgisi: {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="Kullanıcı Adı", value=f"{user.name}", inline=True)
        embed.add_field(name="Görünen Ad", value=f"{user.display_name}", inline=True)
        embed.add_field(name="ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="Hesap Oluşturma Tarihi", value=f"📅 {hesap_tarihi}", inline=False)

        if member:
            katilma_tarihi = member.joined_at.strftime("%d %B %Y, %H:%M")
            embed.add_field(name="Sunucuya Katılma Tarihi", value=f"📥 {katilma_tarihi}", inline=False)
            embed.add_field(name="En Yüksek Rol", value=member.top_role.mention, inline=False)

        embed.set_footer(text="Bot tarafından istendi", icon_url=bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send("❌ Belirttiğin ID'ye sahip bir kullanıcı bulunamadı! (ID'yi yanlış girmiş olabilirsin).")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {e}")

# BOT TOKEN'INI BURAYA YAPIŞTIR (Tırnak işaretlerini silme)
bot.run("")
