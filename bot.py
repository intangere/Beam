import irx.config
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from irx import Irx
from beam import Beam

class Iris(irc.IRCClient):

	nickname = irx.config.nickname
	realname = irx.config.realname
	username = irx.config.username

	def __init__(self):
		self.irx = Irx.Irx(self.sendLine, irx.config.nickname, irx.config.username, irx.config.realname)
		self.irx.loadPlugins("plugins")
		self.irx.buildCommandList()
		self.beam = Beam()
	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
	
	def connectionLost(self):
		irc.IRCClient.connectionLost(self, reason)
	
	def signedOn(self):
		for channel in irx.config.channels:
			self.join(channel)
	
	def topicUpdated(self, user, channel, topic):
		f = open("data/topics/current_topic_%s.txt" % channel, "w+")
		f.write(topic)
		f.close()

	def privmsg(self, user, channel, data):
		if data.startswith("."):
			self.irx.doCommand(channel, user, data)
		else:
			if not data.startswith('%s:' % irx.config.nickname):
				if 'headsplitter' not in user:
					if data.count('.') > 1:
						data = data.split('.')
						for line in data:
							self.beam.addToChain(line)
					else:
						self.beam.addToChain(data)
			else:
				    try:
				        self.irx.send(channel, '%s: %s' % (user.split('!', 1)[0], self.beam.generateRandomText()))
				        #self.irx.send(channel, '%s: %s' % (user.split('!', 1)[0], self.beam.generateText(data.split('%s:' % irx.config.nickname, 1)[1].strip()))) This is seeded with your message
				    except IndexError:
					pass
class BotFactory(protocol.ClientFactory):

	def buildProtocol(self, addr):
		iris = Iris()
		iris.factory = self
		return iris
	
	def clientConnectionFailed(self, connector, reason):
		connector.connect()
	
	def clientConnectionLost(self, connector, reason):
		reactor.stop()

if __name__ == "__main__":
	Factory = BotFactory()
	reactor.connectTCP(irx.config.host, irx.config.port, Factory)
	reactor.run()
