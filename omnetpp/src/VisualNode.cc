#include <omnetpp.h>

using namespace omnetpp;

class VisualNode : public cSimpleModule {
  protected:
    void initialize() override {
        getDisplayString().setTagArg("t", 0, par("label").stringValue());
    }

    void handleMessage(cMessage *msg) override {
        delete msg;
    }
};

Define_Module(VisualNode);
