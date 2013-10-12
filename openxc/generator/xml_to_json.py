import logging

from openxc.utils import fatal_error
from .structures import Signal, Message

LOG = logging.getLogger(__name__)

class Network(object):
    """Represents all the messages on a single bus in an XML-backed database."""

    def __init__(self, database_name, tree, all_messages):
        self.messages = {}

        for message_id, message in all_messages.items():
            message_id = int(message_id, 0)
            query = "./Node/TxMessage[ID=\"0x%s\"]"
            # Search for both lower and upper case hex
            for attr_value in ["%X", "%x"]:
                node = tree.find(query % (attr_value % message_id))
                if node is not None:
                    break
            if node is None:
                LOG.warning("Unable to find message ID 0x%x in %s" % (message_id,
                  database_name))
            else:
                self.messages[message_id] = XMLBackedMessage.from_xml_node(
                    node, message['signals'])

    def to_dict(self):
        return {'messages': dict(("0x%x" % message.id,
                    message.to_dict())
                for message in list(self.messages.values())
                if len(message.signals) > 0)}

class XMLBackedMessage(Message):

    @classmethod
    def from_xml_node(cls, node, mapped_signals):
        message = cls()

        message.name = node.find("Name").text
        message.id = int(node.find("ID").text, 0)

        for signal_name in mapped_signals.keys():
            mapped_signal_node = node.find("Signal[Name=\"%s\"]" % signal_name)
            if mapped_signal_node is not None:
                mapped_signal = XMLBackedSignal.from_xml_node(mapped_signal_node)
                mapped_signal.generic_name = signal_name
                message.signals[signal_name] = mapped_signal

        return message

class XMLBackedSignal(Signal):

    @classmethod
    def from_xml_node(cls, node):
        """Construct a Signal instance from an XML node exported from a Vector
        CANoe .dbc file."""
        return cls(name=node.find("Name").text,
                bit_position=int(node.find("Bitposition").text),
                bit_size=int(node.find("Bitsize").text),
                factor=float(node.find("Factor").text),
                offset=float(node.find("Offset").text),
                min_value=float(node.find("Minimum").text),
                max_value=float(node.find("Maximum").text))


def parse_database(database_filename):
    try:
      from lxml import etree
    except ImportError:
      LOG.warning("Install the 'lxml' Python package to speed up CAN database parsing")
      try:
        # Python 2.5
        import xml.etree.cElementTree as etree
      except ImportError:
        try:
          # Python 2.5
          import xml.etree.ElementTree as etree
        except ImportError:
          try:
            # normal cElementTree install
            import cElementTree as etree
          except ImportError:
            try:
              # normal ElementTree install
              import elementtree.ElementTree as etree
            except ImportError:
              fatal_error("Failed to import ElementTree from any known place")
    return etree.parse(database_filename)


def merge_database_into_mapping(database_filename, database_tree, messages):
    if len(messages) == 0:
        LOG.warning("No messages specified for mapping from XML")
        return {}
    else:
        return Network(database_filename, database_tree, messages).to_dict()
