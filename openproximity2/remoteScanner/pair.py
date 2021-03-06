#!/usr/bin/python
#testing pairing service

import gobject

import sys
import dbus
import dbus.service
import dbus.mainloop.glib

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	exit_on_release = True

	def set_exit_on_release(self, exit_on_release):
		self.exit_on_release = exit_on_release

	@dbus.service.method("org.bluez.Agent",
					in_signature="", out_signature="")
	def Release(self):
		print "Release"
		if self.exit_on_release:
			mainloop.quit()

	@dbus.service.method("org.bluez.Agent",
					in_signature="os", out_signature="")
	def Authorize(self, device, uuid):
		print "Authorize (%s, %s)" % (device, uuid)

	@dbus.service.method("org.bluez.Agent",
					in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print "RequestPinCode (%s)" % (device)
		return "1234"

	@dbus.service.method("org.bluez.Agent",
					in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		print "RequestPasskey (%s)" % (device)
		return dbus.UInt32("1234")

	@dbus.service.method("org.bluez.Agent",
					in_signature="ou", out_signature="")
	def DisplayPasskey(self, device, passkey):
		print "DisplayPasskey (%s, %d)" % (device, passkey)

	@dbus.service.method("org.bluez.Agent",
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		print "RequestConfirmation (%s, %d)" % (device, passkey)
		confirm = raw_input("Confirm passkey (yes/no): ")
		if (confirm == "yes"):
			return
		raise Rejected("Passkey doesn't match")

	@dbus.service.method("org.bluez.Agent",
					in_signature="s", out_signature="")
	def ConfirmModeChange(self, mode):
		print "ConfirmModeChange (%s)" % (mode)

	@dbus.service.method("org.bluez.Agent",
					in_signature="", out_signature="")
	def Cancel(self):
		print "Cancel"

def create_device_reply(device):
	print "New device (%s)" % (device)
	mainloop.quit()

def create_device_error(error):
	print "Creating device failed: %s" % (error)
	mainloop.quit()

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
							"org.bluez.Manager")

	if len(sys.argv) > 1:
		path = manager.FindAdapter(sys.argv[1])
	else:
		path = manager.DefaultAdapter()

	adapter = dbus.Interface(bus.get_object("org.bluez", path),
							"org.bluez.Adapter")

	path = "/test/agent"
	agent = Agent(bus, path)

	mainloop = gobject.MainLoop()

	if len(sys.argv) > 2:
		if len(sys.argv) > 3:
			device = adapter.FindDevice(sys.argv[2])
			adapter.RemoveDevice(device)

		agent.set_exit_on_release(False)
		adapter.CreatePairedDevice(sys.argv[2], path, "DisplayYesNo",
					reply_handler=create_device_reply,
					error_handler=create_device_error)
	else:
		adapter.RegisterAgent(path, "DisplayYesNo")
		print "Agent registered"

	mainloop.run()

	#adapter.UnregisterAgent(path)
	#print "Agent unregistered"

