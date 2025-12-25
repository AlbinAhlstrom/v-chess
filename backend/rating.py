import math
from v_chess.enums import Color

# Glicko-2 constants
TAU = 0.5

class Glicko2Player:
    def __init__(self, rating=1500.0, rd=350.0, volatility=0.06):
        self.mu = (rating - 1500.0) / 173.7178
        self.phi = rd / 173.7178
        self.sigma = volatility

    def get_rating(self):
        return (self.mu * 173.7178) + 1500.0

    def get_rd(self):
        return self.phi * 173.7178

    def _g(self, phi):
        return 1.0 / math.sqrt(1.0 + 3.0 * (phi**2) / (math.pi**2))

    def _E(self, mu, mu_j, phi_j):
        return 1.0 / (1.0 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def update(self, opponent_mu, opponent_phi, outcome):
        g_phi = self._g(opponent_phi)
        E_val = self._E(self.mu, opponent_mu, opponent_phi)
        v = 1.0 / (g_phi**2 * E_val * (1.0 - E_val))
        delta = v * g_phi * (outcome - E_val)
        a = math.log(self.sigma**2)
        
        def f(x):
            term1 = math.exp(x) * (delta**2 - self.phi**2 - v - math.exp(x)) / (2.0 * (self.phi**2 + v + math.exp(x))**2)
            term2 = (x - a) / (TAU**2)
            return term1 - term2

        epsilon = 0.000001
        A = a
        if delta**2 > self.phi**2 + v:
            B = math.log(delta**2 - self.phi**2 - v)
        else:
            k = 1
            while f(a - k * TAU) < 0:
                k += 1
            B = a - k * TAU

        fA = f(A)
        fB = f(B)
        while abs(B - A) > epsilon:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)
            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2.0
            B = C
            fB = fC
        
        new_sigma = math.exp(B / 2.0)
        phi_star = math.sqrt(self.phi**2 + new_sigma**2)
        new_phi = 1.0 / math.sqrt(1.0 / phi_star**2 + 1.0 / v)
        new_mu = self.mu + new_phi**2 * g_phi * (outcome - E_val)

        self.mu = new_mu
        self.phi = new_phi
        self.sigma = new_sigma

async def update_game_ratings(session, game_model, winner_color: str | None):
    from sqlalchemy import select
    from .database import Rating
    
    if not game_model.white_player_id or not game_model.black_player_id:
        return

    async def get_rating_obj(user_id, variant):
        stmt = select(Rating).where(Rating.user_id == user_id, Rating.variant == variant)
        res = await session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            obj = Rating(user_id=user_id, variant=variant)
            session.add(obj)
            await session.flush()
        return obj

    white_rating_obj = await get_rating_obj(game_model.white_player_id, game_model.variant)
    black_rating_obj = await get_rating_obj(game_model.black_player_id, game_model.variant)

    w_p = Glicko2Player(white_rating_obj.rating, white_rating_obj.rd, white_rating_obj.volatility)
    b_p = Glicko2Player(black_rating_obj.rating, black_rating_obj.rd, black_rating_obj.volatility)

    outcome = 1.0 if winner_color == 'w' else (0.0 if winner_color == 'b' else 0.5)

    w_p.update(b_p.mu, b_p.phi, outcome)
    b_p.update(w_p.mu, w_p.phi, 1.0 - outcome)

    white_rating_obj.rating, white_rating_obj.rd, white_rating_obj.volatility = w_p.get_rating(), w_p.get_rd(), w_p.sigma
    black_rating_obj.rating, black_rating_obj.rd, black_rating_obj.volatility = b_p.get_rating(), b_p.get_rd(), b_p.sigma
    
    await session.flush()
