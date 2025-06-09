import torch
import torch.nn as nn

class TimetableAutoencoder(nn.Module):
    def __init__(self, input_dim, param_dim, embed_dim, hidden_dim):
        super(TimetableAutoencoder, self).__init__()
        self.encoder = nn.LSTM(input_dim + param_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc_z = nn.Linear(hidden_dim * 2, embed_dim)
        self.decoder = nn.LSTM(embed_dim + param_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, input_dim)

    def forward(self, x, p):
        B, T, _ = x.size()
        p_exp = p.unsqueeze(1).expand(-1, T, -1) if p.size(1) > 0 else x.new_zeros((B, T, 0))
        enc_input = torch.cat([x, p_exp], dim=-1)
        enc_out, _ = self.encoder(enc_input)
        z = torch.tanh(self.fc_z(enc_out[:, -1, :]))
        z_exp = z.unsqueeze(1).repeat(1, T, 1)
        dec_input = torch.cat([z_exp, p_exp], dim=-1)
        dec_out, _ = self.decoder(dec_input)
        return self.output(dec_out)

def load_model(model_path, input_dim=3, param_dim=0, embed_dim=64, hidden_dim=128):
    model = TimetableAutoencoder(input_dim, param_dim, embed_dim, hidden_dim)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model
